#!/bin/env python

import os, string, sys, shutil, commands

siteInstallDefaultParams = {
    "TargetDir":"./opt",
    "WebWareVersion":"0.9.2",
    "LapVersion":"0.8.0-20061026",
    "LapAppDirName":"lap"
}

siteInstallDefaultDescriptions = {
    "TargetDir":"Target installation directory",
    "WebWareVersion":"WebWare version",
    "LapVersion":"Portal version",
    "LapAppDirName":"Portal application directory name"
}

siteConfigDefaultParams = {
    "LogFile":"/var/log/lap/lap.log",
    "InitLogFile":"/var/log/lap/lap_init.log",
    "WebWareLogFile":"/var/log/lap/lap_ww.log",
    "PluginDir":"/opt/lap/context/Plugins",
    "SessionDir":"/var/spool/lap",
    "WebWareDir":"/opt/Webware-0.9.2",
    "AppWorkDir":"/opt/lap",
    "DependsDir":"/opt/lap/depends",
    "NorduGridDir":"/opt/nordugrid",
    "VOAdmin":"/O=Grid/O=NorduGrid/OU=byggmek.lth.se/CN=Jonas Lindemann",
    "SMTPServer":"mail.lth.se",
    "ServerUser":"portaluser",
    "ServerGroup":"lunarc",
    "ServerPIDFile":"/var/run/lap.pid"
}

siteConfigDefaultDescriptions = {
    "LogFile":"Portal log file",
    "InitLogFile":"Portal startup log file",
    "WebWareLogFile":"WebWare log file",
    "PluginDir":"Portal plugin directory",
    "SessionDir":"Portal job session directory",
    "WebWareDir":"WebWare installation directory",
    "AppWorkDir":"Portal installation directory",
    "DependsDir":"Portal dependency installation directory",
    "NorduGridDir":"NorduGrid ARC installation directory",
    "VOAdmin":"Portal Virtual Organisation administrator",
    "SMTPServer":"Default mail server",
    "ServerUser":"Portal user id",
    "ServerGroup":"Portal group id",
    "ServerPIDFile":"Portal process id file"
}

    
siteConfigTemplate = """Application = {
        "ContextName":"context"
}

Logging = {
        "LogFile":"%(LogFile)s",
        "WebWareLogFile":"%(WebWareLogFile)s"
}

Dirs = {
    "PluginDir":"%(PluginDir)s",
    "SessionDir":"%(SessionDir)s",
    "WebWareDir":"%(WebWareDir)s",
    "AppWorkDir":"%(AppWorkDir)s",
    "DependsDir":"%(DependsDir)s",
    "NorduGridDir":"%(NorduGridDir)s"
}

Appearance = {
        "WelcomeMessage":"Welcome to the LUNARC application portal",
        "WebSiteName":"LUNARC",
        "LogoImage":"images/logo.png",
        "LogoImageWidth":"445px",
        "LogoImageHeight":"86px"
}

Admin = {
        "VOAdmin":"%(VOAdmin)s",
        "VOSites":["130.235.7.91"]
}

System = {
        "SMTPServer":"%(SMTPServer)s",
        "ServerUser":"%(ServerUser)s",
        "ServerGroup":"%(ServerGroup)s",
        "ServerPIDFile":"%(ServerPIDFile)s"
}
"""

apacheConfigTemplate = """LoadModule webkit_module modules/mod_webkit.so

<Location /%(Location)s>
WKServer localhost 8086
SetHandler webkit-handler
SSLRequireSSL
</Location>
"""

class OptionInput:
    def __init__(self, options = {}, descriptions = {}, caption = ""):
        self._options = options
        self._descriptions = descriptions
        self._caption = caption
        
    def setOptions(self, options):
        self._options = options
        
    def setDescriptions(self, descriptions):
        self._descriptions = descriptions
        
    def setCaption(self, caption):
        self._caption = caption
        
    def execute(self):
        
        choice = 1
        choiceInput = "1"
        
        # Check max description width
        
        maxLen = -1
        
        for key in self._descriptions.keys():
            if len(self._descriptions[key])>maxLen:
                maxLen = len(self._descriptions[key])
        
        while choice > 0:

            print        
            print self._caption
            print
            keys = self._options.keys()
            keys.sort()
            
            number = 1
            
            for key in keys:
                print "\t"+str(number)+". "+" "*(2-len(str(number)))+self._descriptions[key]+" "*(maxLen-len(self._descriptions[key])+4)+": "+self._options[key]
                number = number + 1
        
            print

            choice = -1
            choiceInput = raw_input("Enter option to change. (Enter = accept, 0 = quit) :")
            
            if choiceInput == '':
                break
            
            try:
                choice = int(choiceInput)
            except:
                choice = 1
                continue
                
            print choice
                  
            if choice > 0 and choice <= len(keys):
                print
                print self._descriptions[keys[choice-1]]+" = "+self._options[keys[choice-1]]
                print
                newValue = raw_input("New value (Enter = No Change) : ")
                
                if newValue<>"":
                    self._options[keys[choice-1]] = newValue
                    
        if choice==0:
            return None
        else:
            return self._options
        
class SystemCheck:
    def __init__(self):
        self._haveWget = False
        self._haveTar = False
        self._haveUname = False
        self._haveGunzip = False
        self._haveARC = False
        self._haveAPXS = False
        self._haveARCLib = False
        
        self._arcInstallDir = ""
        
        self._doCheck()
        
    def _findOnPath(self, executable):

        systemPath = os.environ['PATH']
        
        systemPath = systemPath + ":/sbin:/usr/sbin"

        for item in systemPath.split(':'):
            try:
                if executable in os.listdir(item):
                    return True
            except OSError:
                pass

        return False
    
    def _findPath(self, executable):

        systemPath = os.environ['PATH']

        for item in systemPath.split(':'):
            try:
                if executable in os.listdir(item):
                    return item
            except OSError:
                pass

        return ""

    def _checkCommand(self, command, alternateText = "", resolution = ""):
        if alternateText=="":
            print "Checking for", command+".",
        else:
            print "Checking for", alternateText+".",
        result = self._findOnPath(command)
        if result:
            print "Found."
        else:
            print "Not found."
            if resolution !="":
                print
                print "\t"+resolution
                print
        
        return result
    
    def _checkInstallDir(self, command, alternateText = "", resolution = ""):
        if alternateText=="":
            print "Checking for", command+".",
        else:
            print "Checking for", alternateText+".",
        result = self._findPath(command)
        result = result.split("/bin")[0]
        
        if result:
            self._arcInstallDir = result
            print "Found."
        else:
            print "Not found."
            if resolution !="":
                print
                print "\t"+resolution
                print
        
        return result
    
    def _checkARCLib(self):
        print "Checking for Python based ARCLib.",
        if self._arcInstallDir !="":
            # /lib/python2.3/site-packages
            if os.path.isdir(self._arcInstallDir+"/lib/python2.3/site-packages"):
                print "Found."
                return True
            elif os.path.isdir(self._arcInstallDir+"/lib/python2.4/site-packages"):
                print "Found."
                return True
            elif os.path.isdir(self._arcInstallDir+"/lib/python2.5/site-packages"):
                print "Found."
                return True
            else:
                print "Not found."
                print
                print "Please add the following packages to the ARC install:"
                print
                print "\tnordugrid-arc-python-0.5.x"
                print "\tnordugrid-arc-libs-devel-0.5.x"
                print 
            
        else:
            print "Not found."
            return True
           
    def _doCheck(self):
        
        print
        print "---------------------------------------"
        print "Checking for prerequisites."
        print "---------------------------------------"
        print
        
        self._haveWget = self._checkCommand("wget")
        self._haveTar = self._checkCommand("tar")
        self._haveUname = self._checkCommand("uname")
        self._haveGunzip = self._checkCommand("gunzip")
        self._haveARC = self._checkCommand("ngsub", "ARC client tools", "Please install the ARC client, see http://www.nordugrid.org.")
        self._haveAPXS = self._checkCommand("apxs", "Apache Extension Tool (APXS)",
                                            "APXS is needed to build the WebWare apache module. \n\tIt is often found in the httpd-devel package on RedHat derived distros.")
        self._arcInstallDir = self._checkInstallDir("ngsub", "ARC installation dir")
        
        self._haveARCLib = self._checkARCLib()
        
    def haveWget(self):
        return self._haveWget
    
    def haveTar(self):
        return self._haveTar
    
    def haveUname(self):
        return self._haveUname
    
    def haveGunzip(self):
        return self._haveGunzip
    
    def haveARC(self):
        return self._haveARC
    
    def getARCInstallDir(self):
        return self._arcInstallDir
    
    def requirementsOk(self):
        return self._haveWget and self._haveTar and self._haveUname and self._haveGunzip and self._haveARC and self._haveAPXS and self._haveARCLib
        

class DownloadError(Exception):
    pass

class ExtractionError(Exception):
    pass

class Package:
    def __init__(self):
        self._targetDir = "./opt"
        self._version = "1.0"
        self._downloadURL = ""
        self._fileList = []
        self._extractTool = "tar"
        self._packageDir = "./packages"
        self._osFlavor = "rhel"
        self._osMajorVersion = 4
        self._osMinorVersion = 4
        
    def setOS(self, flavor, majorVersion, minorVersion):
        self._osFlavor = "rhel"
        self._osMajorVersion = 4
        self._osMinorVersion = 4
        
    def getOS(self):
        return self._osFlavor, self._osMajorVersion, self._osMinorVersion
    
    def getOSFlavor(self):
        return self._osFlavor
    
    def getOSMajorVersion(self):
        return self._osMajorVersion
    
    def getOSMinorVersion(self):
        return self._osMinorVersion

    def setTargetDir(self, targetDir):
        if not os.path.exists(targetDir):
            os.mkdir(targetDir)
        self._targetDir = targetDir
        
    def setVersion(self, version):
        self._version = version
        
    def setDownloadURL(self, downloadURL):
        self._downloadURL = downloadURL
        
    def addFile(self, filename):
        self._fileList.append(filename)
        
    def download(self):
        if not os.path.exists(self._packageDir):
            os.mkdir(self._packageDir)
            
        for filename in self._fileList:
            realFilename = filename % self._version
            print "--> " + realFilename + " ", 
            if not os.path.exists(os.path.join(self._packageDir, realFilename)):
                url = os.path.join(self._downloadURL, realFilename)
                status = os.system("wget -q -P " + self._packageDir+ " " + url)
                
                if status == 0:
                    print "\t\t[Downloaded]"
                else:
                    print "\t\t[Download failed]"
                    raise DownloadError()
            else:
                print "\t\t[Exists]"
                
    def extract(self):
        if not os.path.exists(self._targetDir):
            os.mkdir(self._targetDir)
            
        for filename in self._fileList:
            realFilename = filename % self._version
            status = os.system("tar xzf %s -C %s" % (os.path.join(self._packageDir, realFilename), self._targetDir))
            
            if status <> 0:
                raise ExtractionError()
            
    def getInstallDir(self, idx):
        if idx>=0 and idx<len(self._fileList):
            realFilename = self._fileList[idx] % self._version
            packageDir, ext = os.path.splitext(realFilename)
            packageDir, ext = os.path.splitext(packageDir)
            packageDir = os.path.join(self._targetDir, packageDir)
            return packageDir
        else:
            return ""
        
    def getDownloadURL(self):
        return self._downloadURL
    
    def setup(self):
        pass
    
class WebWare(Package):
    def __init__(self):
        Package.__init__(self)
        self._apacheConfigDir = "/etc/httpd"
        self._redhatBased = True
        self.setVersion("0.9.2")
        self.setDownloadURL("http://heanet.dl.sourceforge.net/sourceforge/webware")
        self.addFile("Webware-%s.tar.gz")
        
    def setApacheConfigDir(self, configDir):
        self._apacheConfigDir = configDir        
            
    def setup(self):
        realFilename = self._fileList[0] % self._version
        packageDir, ext = os.path.splitext(realFilename)
        packageDir, ext = os.path.splitext(packageDir)
        packageDir = os.path.join(self._targetDir, packageDir)
        print packageDir
        if os.path.exists(packageDir):
            currDir = os.getcwd()
            os.chdir(packageDir)
            os.system("python ./install.py --no-password-prompt")
            os.chdir(currDir)
            
    def createAppDir(self, appDir):
        realAppDir = os.path.abspath(appDir)
        webwareDir = self.getInstallDir(0)
        currDir = os.getcwd()
        os.chdir(webwareDir+"/bin")
        cmd = "./MakeAppWorkDir.py -c context " + realAppDir
        print "Executing, ", cmd
        os.system(cmd)
        os.chdir(currDir)
        
    def buildApacheModule(self):
        webwareDir = self.getInstallDir(0)
        currDir = os.getcwd()
        os.chdir(webwareDir+"/WebKit/Adapters/mod_webkit2")
        print os.system("make")
        print os.system("make install")
        os.chdir(currDir)
                
               
class AppPortal(Package):
    def __init__(self):
        Package.__init__(self)
        self._webwareDir = ""
        self._configParams = {}
        self._installParams = {}
        self.setVersion("0.8.0-20061026")
        self.setDownloadURL("http://grid.lunarc.lu.se/lapsrc")
        self.addFile("lap-config-%s.tar.gz")
        self.addFile("lap-layout-%s.tar.gz")
        self.addFile("lap-plugins-%s.tar.gz")
        self.addFile("lap-source-%s.tar.gz")
        
    def setWebwareDir(self, webwareDir):
        self._webwareDir = webwareDir
        
    def setConfigParams(self, configParams):
        self._configParams = configParams
        
    def setInstallParams(self, installParams):
        self._installParams = installParams
        
    def createSiteConfig(self):
        configFilename = self._targetDir+"/LapConfig/LapSite.py"
        
        configFile = file(configFilename, "w")
        configFile.write(configFilename % self._configParams)
        configFile.close()
        
    def updateInitFile(self):
        initFilename = self._targetDir+"/init/lap"
        
        initFile = file(initFilename, "r")
        lines = initFile.readlines()
        initFile.close()
        
        # WEBKIT_DIR=/sw/lap
        # PID_FILE=/var/run/lap.pid
        # LOG=/var/log/lap/lap_init.log
        
        initFile = file(initFilename, "w")
        
        appDirDone = False
        pidFileDone = False
        logFileDone = False
        
        for line in lines:
            newLine = line
            if line.find("APP_DIR")<>-1 and not appDirDone:
                newLine = "APP_DIR="+self._targetDir+"\n"
                appDirDone = True
            if line.find("PID_FILE")<>-1 and not pidFileDone:
                newLine = "PID_FILE="+self._configParams["ServerPIDFile"]+"\n"
                pidFileDone = True
            if line.find("LOG")<>-1 and not logFileDone:
                newLine = "LOG="+self._configParams["InitLogFile"]+"\n"
                logFileDone = True
            
            initFile.write(newLine)
        
        initFile.close()
        
    def createApacheConfig(self, location = "lap", rootInstall = False):
        
        apacheConfigFilename = ""

        if self.getOSFlavor() == "rhel" and rootInstall:
            
            # On RedHat we use the conf.d directory to add
            # configuration to the apache web server
            
            apacheConfigFilename = "/etc/httpd/conf.d/ssl_lap.conf"
           
        else:
            
            # For other distros we just create the config file
            # in the current directory
            
            apacheConfigFilename = "./ssl_lap.conf"
            
        configFile = file(apacheConfigFilename, "w")
        configFile.write(apacheConfigTemplate % {"Location":location})
        configFile.close()
        
def main():
    
    installWebWare = True
    downloadPortal = True
    buildApacheModule = True
    
    # Check requirements
    
    systemCheck = SystemCheck()
    if not systemCheck.requirementsOk():
        sys.exit(-1)
        
    norduGridDir = systemCheck.getARCInstallDir()

    print    
    print "---------------------------------------"
    print "Lunarc Application Portal - Setup 0.1"
    print "---------------------------------------"
    
    installOptions = OptionInput()
    installOptions.setOptions(siteInstallDefaultParams)
    installOptions.setDescriptions(siteInstallDefaultDescriptions)
    installOptions.setCaption("Please set the installation options:")
    installParams = installOptions.execute()
    
    if installParams == None:
        sys.exit(-1)
        
    installParams["TargetDir"] = os.path.abspath(installParams["TargetDir"])
    
    print
    print
    print "---------------------------------------"
    print "Installing WebWare for Python"
    print "---------------------------------------"
    print
    webware = WebWare()
    webware.setVersion(installParams["WebWareVersion"])
    webware.setTargetDir(installParams["TargetDir"])
    
    if installWebWare:
        try:
            print "Downloading WebWare..."
            webware.download()
            print "Extracting WebWare..."
            webware.extract()
            print "Setting up WebWare..."
            webware.setup()
        except DownloadError:
            print 
            print "Failed to download WebWare from:"
            print 
            print "\t", webware.getDownloadURL()
            print
            sys.exit(-1)
        except ExtractionError:
            print
            print "Failed to extract WebWare."
            print
            sys.exit(-1)
        except:
            print 
            print "Unexpected error:", sys.exc_info()[0]
            print 
    
    webwareInstallDir = webware.getInstallDir(0)
    print "Webware installed at: ", webwareInstallDir
    
    print "---------------------------------------"
    print "Building WebWare Apache Module"
    print "---------------------------------------"
    print
    
    if buildApacheModule:
        webware.buildApacheModule()
    
    print "---------------------------------------"
    print "Creating WebWare application instance"
    print "---------------------------------------"
    print
    
    ApplicationDir = os.path.join(installParams["TargetDir"], installParams["LapAppDirName"])
    
    print "Creating application dir..."
    webware.createAppDir(ApplicationDir)
    
    print "---------------------------------------"
    print "Downloading Lunarc Application portal"
    print "---------------------------------------"
    print

    portal = AppPortal()
    portal.setTargetDir(ApplicationDir)
    portal.setVersion(installParams["LapVersion"])
    
    if downloadPortal:
        try:
            print "Downloading portal..."
            portal.download()
            print "Extracting portal..."
            portal.extract()
        except DownloadError:
            print 
            print "Failed to download Portal from:"
            print 
            print "\t", portal.getDownloadURL()
            print
            sys.exit(-1)
        except ExtractionError:
            print
            print "Failed to extract WebWare."
            print
            sys.exit(-1)
        except:
            print 
            print "Unexpected error:", sys.exc_info()[0]
            print
            sys.exit(-1)
            
        
    print
    print "---------------------------------------"
    print "Downloading and installing dependencies"
    print "---------------------------------------"
    print

    currDir = os.getcwd()
    os.chdir(ApplicationDir)
    
    status = os.system("./install-depends")
    if status != 0:
        print
        print "Dependency install failed."
        print
        sys.exit(-1)
        
    os.chdir(currDir)
    
    print
    print "---------------------------------------"
    print "Configuring Lunarc Application Portal"
    print "---------------------------------------"
    
    siteConfigDefaultParams["PluginDir"] = os.path.join(ApplicationDir, "context/Plugins")
    siteConfigDefaultParams["WebWareDir"] = os.path.join(installParams["TargetDir"], "Webware-%s" % installParams["WebWareVersion"])
    siteConfigDefaultParams["AppWorkDir"] = ApplicationDir
    siteConfigDefaultParams["DependsDir"] = os.path.join(ApplicationDir, "depends")
    siteConfigDefaultParams["NorduGridDir"] = norduGridDir

    siteConfigInput = OptionInput()
    siteConfigInput.setOptions(siteConfigDefaultParams)
    siteConfigInput.setDescriptions(siteConfigDefaultDescriptions)
    siteConfigInput.setCaption("Please set the portal configuration options:")
    siteConfigParams = siteConfigInput.execute()
    
    if siteConfigParams == None:
        sys.exit(-1)

    print 
    print "Creating configuration..."
    portal.setConfigParams(siteConfigParams)
    portal.createSiteConfig()
    portal.updateInitFile()
    portal.createApacheConfig(location="lap", rootInstall = False)

if __name__ == "__main__":
    
    main()
