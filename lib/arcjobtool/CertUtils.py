"""
Module for certificate utilities.
"""

import sys, os, getpass, datetime, re, smtplib, shutil

from subprocess import *
from email.MIMEText import MIMEText

directionsTemplate = """Please read the instructions below carefully!

This is a Certificate Request file. It should be mailed to your local
registration authority (RA) for identity validation. You can find the
list of approved RAs at:

    http://hep.nbi.dk/CA/

=========================================================================

A private key and a certificate request has been generated with the
subject:

    %(SUBJECT)

The above string (without the emailaddress field if present) is known
as your %(SERVICE) certificate subject, and uniquely identifies
this %(SERVICE) inside the NorduGrid CA.

If the subject above is not appropriate, rerun this script with
the -force and -int options.

Your private key is stored in %(KEY_FILE)
Your request is stored in %(REQUEST_FILE)

Your certificate will be mailed to you within 7 working days after it
has been recieved by the NorduGrid CA.

If you have any questions about the certificate contact
the %(GSI_CA_NAME) at %(GSI_CA_EMAIL_ADDR)

"""

# Ported from Recipe 3.9 in Secure Programming Cookbook for C and C++ by
# John Viega and Matt Messier (O'Reilly 2003)

rfc822_specials = '()<>@,;:\\"[]'

def isValidEmail(addr):
    # First we validate the name portion (name@domain)
    c = 0
    while c < len(addr):
        if addr[c] == '"' and (not c or addr[c - 1] == '.' or addr[c - 1] == '"'):
            c = c + 1
            while c < len(addr):
                if addr[c] == '"': break
                if addr[c] == '\\' and addr[c + 1] == ' ':
                    c = c + 2
                    continue
                if ord(addr[c]) < 32 or ord(addr[c]) >= 127: return 0
                c = c + 1
            else: return 0
            if addr[c] == '@': break
            if addr[c] != '.': return 0
            c = c + 1
            continue
        if addr[c] == '@': break
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127: return 0
        if addr[c] in rfc822_specials: return 0
        c = c + 1
    if not c or addr[c - 1] == '.': return 0

    # Next we validate the domain portion (name@domain)
    domain = c = c + 1
    if domain >= len(addr): return 0
    count = 0
    while c < len(addr):
        if addr[c] == '.':
            if c == domain or addr[c - 1] == '.': return 0
            count = count + 1
        if ord(addr[c]) <= 32 or ord(addr[c]) >= 127: return 0
        if addr[c] in rfc822_specials: return 0
        c = c + 1

    return count >= 1

class CertificateRequest(object):
    """
    Class for generating a grid certificate request.
    
    Basic structure and procedures are modeled after the grid-cert-request
    script from the Globus project.
    """
    def __init__(self, domain="", name="", email=""):
        """
        Class constructor
        """
        self.domain = domain
        self.name = name
        self.email = email
        self.CAName = ""
        self.CAEmail = ""

        # Properties for sending signing request

        self.emailTo = ""
        self.emailFrom = ""
        self.emailSubject = "Certificate Request"
        self.emailSMTPServer = "localhost"
        
        self.keyFilename = "userkey.pem"
        self.certFilename = "usercert.pem"
        self.certRequestFilename = "usercert_request.pem"
        self.randomFilename = "uicertreq.random"
        self.passphrase = ""
        self.globusUserConfig = "/etc/grid-security/globus-user-ssl.conf"
        self.gridSecurityConfig = "/etc/grid-security/grid-security.conf"
        self.directionsFilename = "/etc/grid-security/directions"
        self.directionsStartHeader = "----- BEGIN REQUEST HEADER TEXT -----"
        self.directionsEndHeader = "----- END REQUEST HEADER TEXT -----"
        
        self.currentRequestDir = ""
        
        self.directionsTemplate = directionsTemplate
        
        self.requestCmdTemplate = "openssl req -new -keyout %s -out %s -rand %s -config %s -passout stdin 2> /dev/null"
        
        self.haveCAInfo = self.__readCAInfo()
        
        self.__setupDefaultDirs()
        
    def __processLine(self, line):
        """
        Convert characters and variables to a Python format.
        """
        
        line = line.replace('"', '')
        line = line.replace("${", "%(")
        line = line.replace("}", ")s")
        return line
    
    def __readCAInfo(self):
        """
        Extract CA info from /etc/grid-security.conf
        """
        
        if not os.path.exists(self.gridSecurityConfig):
            print "No security configuration found. Using program defaults."
            return False
        
        gridSecurityFile = open(self.gridSecurityConfig, "r")
        lines = gridSecurityFile.readlines()
        gridSecurityFile.close()
        
        defaultCAName = ""
        defaultCAEmail = ""
        setupCAName = ""
        setupCAEmail = ""
        
        for line in lines:
            if line.find("SETUP_GSI_CA_NAME")!=-1 and setupCAName=="":
                setupCAName = line.split("=")[1].replace('"','').strip()
            if line.find("SETUP_GSI_CA_EMAIL")!=-1 and setupCAEmail=="":
                setupCAEmail = line.split("=")[1].replace('"','').strip()
            if line.find("DEFAULT_GSI_CA_NAME")!=-1 and defaultCAName=="":
                defaultCAName = line.split("=")[1].replace('"','').strip()
            if line.find("DEFAULT_GSI_CA_EMAIL")!=-1 and defaultCAEmail=="":
                defaultCAEmail = line.split("=")[1].replace('"','').strip()
                
        if setupCAName!="":
            self.CAName = setupCAName
        elif defaultCAName!="":
            self.CAName = defaultCAName
        
        if setupCAEmail!="":
            self.CAEmail = setupCAEmail
        elif defaultCAEmail!="":
            self.CAEmail = defaultCAEmail
            
        return True

    def __readDirectionsText(self):
        """
        Read directions template from /etc/grid-security if it exists.
        """
        
        if os.path.exists(self.directionsFilename):
        
            directionsFile = open(self.directionsFilename, "r")
            lines = directionsFile.readlines()
            directionsFile.close()
            
            directionsTemplate = ""
            
            addLines = False
            
            for line in lines:
                if line.strip() == self.directionsEndHeader:
                    addLines = False
                
                if addLines:
                    line = self.__processLine(line)
                    directionsTemplate += line
                    
                if line.strip() == self.directionsStartHeader:
                    addLines = True
                    
            self.directionsTemplate = directionsTemplate
        else:
            self.directionsTemplate = directionsTemplate
        
    def __createRandomData(self):
        """
        Create semi random data for use when generating keys.
        """
        
        randomData = ""
        randomData += Popen("head -1000 /dev/urandom 2>&1", shell=True, stdout=PIPE).communicate()[0]
        randomData += Popen("date 2>&1", shell=True, stdout=PIPE).communicate()[0]
        randomData += Popen("netstat -in 2>&1", shell=True, stdout=PIPE).communicate()[0]
        randomData += Popen("ps -ef 2>&1", shell=True, stdout=PIPE).communicate()[0]
        randomData += Popen("ls -ln ${HOME} 2>&1", shell=True, stdout=PIPE).communicate()[0]
        randomData += Popen("ls -ln /tmp 2>&1", shell=True, stdout=PIPE).communicate()[0]
        
        randomFile = open(self.randomFilename, "w")
        randomFile.write(randomData)
        randomFile.close()
        
    def __setupDefaultDirs(self):
        """
        Setup default dirs for cert request generation.
        """
        
        self.homeDir = os.getenv("HOME")
        self.globusDir = os.path.join(self.homeDir, ".globus")
        if not os.path.exists(self.globusDir):
            os.mkdir(self.globusDir)
                      
    def __createRequestDir(self):
        """
        Create temporary request directory for storing the new certificate
        request. Format $HOME/.globus/uicertreq.request.XXXXXX
        """
        
        timeStamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        self.requestDir = os.path.join(self.globusDir, "uicertreq.request.%s" % timeStamp)
        os.mkdir(self.requestDir)
        
        self.currentRequestDir = self.requestDir
        
        self.certFilename = os.path.join(self.requestDir, "usercert.pem")
        self.certRequestFilename = os.path.join(self.requestDir, "usercert_request.pem")
        self.keyFilename = os.path.join(self.requestDir, "userkey.pem")
        self.randomFilename = os.path.join(self.requestDir, "uicertreq.random")
        
    def checkPendingRequests(self):
        """
        Check for existing certificate requests.
        """
        
        requestList = []

        if os.path.exists(self.globusDir):
            
            dirItems = os.listdir(self.globusDir)
            
            for item in dirItems:
                fullPath = os.path.join(self.globusDir, item)
                if os.path.isdir(fullPath):
                    if fullPath.find("uicertreq.request")!=-1:
                        requestList.append(fullPath)
            
        return requestList
    
    def loadRequest(self, requestDir):
        """
        Load existing request information.
        """
        
        self.currentRequestDir = requestDir
        
        self.certRequestFilename = os.path.join(requestDir, "usercert_request.pem")
        self.certFilename = os.path.join(requestDir, "usercert.pem")
        self.keyFilename = os.path.join(requestDir, "userkey.pem")
        
        # subject=/O=Grid/O=NorduGrid/OU=lunarc.lu.se/CN=Jonas Lindemann/emailAddress=jonas.lindemann@lunarc.lu.se
        
        self.subject = Popen("openssl req -noout -in %s -subject" % (self.certRequestFilename), shell=True, stdout=PIPE).communicate()[0].strip()
        
        self.subject = self.subject[9:]
        parts = self.subject.split("/")
        
        for part in parts:
            if part.find("CN=")!=-1:
                self.name = part.split("CN=")[1]
            elif part.find("OU=")!=-1:
                self.domain = part.split("OU=")[1]
            elif part.find("emailAddress=")!=-1:
                self.email = part.split("emailAddress=")[1]
        
    def checkPassphrase(self, passphrase):
        strength = ['Blank','Very Weak','Weak','Medium','Strong','Very Strong']
        score = 1
    
        if len(passphrase) < 1:
            return strength[0]
        if len(passphrase) < 4:
            return strength[1]
    
        if len(passphrase) >=6:
            score = score + 1
        if len(passphrase) >=12:
            score = score + 1
        
        if re.search('\d+',passphrase):
            score = score + 1
        if re.search('[a-z]',passphrase) and re.search('[A-Z]',passphrase):
            score = score + 1
        if re.search('.[!,@,#,$,%,^,&,*,?,_,~,-,?,(,)]',passphrase):
            score = score + 1
    
        return strength[score]

    def generate(self, passphrase = ""):
        """
        Generates private key and certificate request.
        """
        
        # Check if we have CA configuration
        
        if not self.haveCAInfo:
            wx.MessageBox("Could not find valid CA configuration files.", "Certificate request")
            return
                
        # We don't do anything if the passphrase is empty
        
        if passphrase == "":
            return
        
        # Create directory for request and setup filenames
        
        self.__createRequestDir()        
        
        # Create semi random data
        
        self.__createRandomData()
        
        # Create response string
        
        inputData = passphrase + "\n"
        inputData += "\n\n"
        inputData += self.domain+"\n"
        inputData += self.name+"\n"
        inputData += self.email+"\n"
        
        # Generate private key and certificate request using OpenSSL
        
        Popen(self.requestCmdTemplate % (self.keyFilename, self.certRequestFilename, self.randomFilename, self.globusUserConfig),
              shell=True, stdout= PIPE, stdin=PIPE).communicate(inputData)[0]
        
        os.chmod(self.keyFilename, 0400)
        os.chmod(self.certRequestFilename, 0600)
        
        # Extract request subject
        
        self.subject = Popen("openssl req -noout -in %s -subject" % (self.certRequestFilename), shell=True, stdout=PIPE).communicate()[0].strip()
        
        # Remove random data file
        
        if os.path.exists(self.randomFilename):
            os.unlink(self.randomFilename)
        
        # Read instructions template
        
        self.__readDirectionsText()
        
        # Read CA information
        
        self.__readCAInfo()
        
        # Create request header
        
        requestHeader = self.directionsTemplate % {"SUBJECT":self.subject, "SERVICE":"user", "GSI_CA_NAME":self.CAName,
                                                   "GSI_CA_EMAIL_ADDR":self.CAEmail, "KEY_FILE":self.keyFilename, "REQUEST_FILE":self.certRequestFilename}
        
        # Read original request
        
        requestFile = open(self.certRequestFilename, "r")
        requestFileContents = requestFile.read()
        requestFile.close()
        
        # Add request header
        
        requestFile = open(self.certRequestFilename, "w")
        requestFile.write(requestHeader)
        requestFile.write(requestFileContents)
        requestFile.close()
        
        self.updateStatus("GENERATED")
        
    def signingStatus(self):
        """
        Return current signing status for loaded request
        """
        
        statusFilename = os.path.join(self.currentRequestDir, "signing.status")
        
        if os.path.exists(statusFilename):
            requestStatusFile = open(statusFilename, "r")
            requestStatus = requestStatusFile.read()
            requestStatusFile.close()
            
            dateString = requestStatus.split(":")[0].strip()
            status = requestStatus.split(":")[1].strip()
            return status, dateString
        else:
            return "UNKNOWN", ""

    def isUnknown(self):
        status, dateString = self.signingStatus()
        return status == "UNKNOWN"        
        
    def isSent(self):
        status, dateString = self.signingStatus()
        return status == "SENT"        
        
    def isSigned(self):
        status, dateString = self.signingStatus()
        return status == "INSTALLED"
    
    def isGenerated(self):
        status, dateString = self.signingStatus()
        return status == "GENERATED"
    
    def isLoaded(self):
        return self.currentRequestDir!=""
    
    def isGlobusConfigOk(self):
        """
        Check that we have needed request configuration files.
        """
        configOk = True
        if not os.path.exists(self.directionsFilename):
            configOk = False
        if not os.path.exists(self.globusUserConfig):
            configOk = False
        if not os.path.exists(self.gridSecurityConfig):
            configOk = False
            
        return configOk
    
    def updateStatus(self, status):
        """
        Update the signing process status.
        """
        statusFilename = os.path.join(self.currentRequestDir, "signing.status")
        timeStamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
        statusFile = open(statusFilename, "w")
        statusFile.write(timeStamp+":"+status)
        statusFile.close()
    
    def sendSigningRequest(self):
        """
        Send certificate request for signing.
        """
        
        # Do we have a certificate request?
        
        if self.currentRequestDir == "":
            return "No request loaded or generated."
        
        # Check for pending signing request
        
        status, dateString = self.signingStatus()
            
        if status == "SENT":
            return "Certificate request was sent "+dateString+"."
               
        # Check input 
        
        if not isValidEmail(self.emailFrom):
            return "Not a valid from address."
        
        if not isValidEmail(self.emailTo):
            return "Not av valid to address."
        
        if self.emailSubject == "":
            return "No subject given"
        
        # Create mail message
        
        requestFile = open(self.certRequestFilename, "r")
        message = MIMEText(requestFile.read())
        requestFile.close()
                
        message['Subject'] = self.emailSubject
        message['From'] = self.emailFrom
        message['To'] = self.emailTo
        
        try:
            s = smtplib.SMTP(self.emailSMTPServer)
            s.sendmail(self.emailFrom, self.emailTo, message.as_string())
            #s.sendmail("jonas.lindemann@lunarc.lu.se", "jonas.lindemann@lunarc.lu.se", message.as_string())
            s.quit()
        except:
            return "Could not send email."
        
        # Write a email receipt file.
        
        self.updateStatus("SENT")
               
        return ""
    
    def updateCertificate(self, certificateText):
        """
        Update certificate file with signed certificate.
        """
        userCertFile = open(self.certFilename, "w")
        userCertFile.write(certificateText)
        userCertFile.close()
        
    def hasExistingCredentials(self):
        """
        Check for existing credentials.
        """
        
        hasKey = os.path.exists(os.path.join(self.globusDir, "userkey.pem"))
        hasCert = os.path.exists(os.path.join(self.globusDir, "usercert.pem"))
        
        return hasKey or hasCert
        
    def installCertAndKey(self):
        """
        Copy user key and certificate into certificate directory.
        Remove certificate request directory.
        """
        realUserKeyFilename = os.path.join(self.globusDir, "userkey.pem")
        realUserCertFilename = os.path.join(self.globusDir, "usercert.pem")
        
        # Rename existing certificate files if any
        
        if os.path.exists(realUserKeyFilename):
            os.rename(realUserKeyFilename, realUserKeyFilename+".old."+datetime.datetime.now().strftime("%Y%m%d-%H%M"))
        
        if os.path.exists(realUserCertFilename):
            os.rename(realUserCertFilename, realUserCertFilename+".old."+datetime.datetime.now().strftime("%Y%m%d-%H%M"))
        
        # Copy generated and signed certificate files from request dir
        
        shutil.copyfile(self.certFilename, realUserCertFilename)
        shutil.copyfile(self.keyFilename, realUserKeyFilename)
        
        # Make sure the permissions are set correctly
        
        os.chmod(realUserKeyFilename, 0400)
        
        self.updateStatus("INSTALLED")
        
    def removeCurrentRequestDir(self):
        """
        Remove current request directory
        """
        if os.path.exists(self.currentRequestDir):
            shutil.rmtree(self.currentRequestDir)
            sself.currentRequestDir = ""
            self.keyFilename = "userkey.pem"
            self.certFilename = "usercert.pem"
            self.certRequestFilename = "usercert_request.pem"
            self.__setupDefaultDirs()
