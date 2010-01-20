#!/bin/env python
#
# myproxy client
#
# Tom Uram <turam@mcs.anl.gov>
# 2005/08/04
#
# Converted to class by
#
# Jonas Lindemann
#
# Original myproxy_logon.py:
# http://www.mcs.anl.gov/research/projects/accessgrid/myproxy/myproxy.html
#


import os
import socket
from OpenSSL import crypto, SSL

class GetException(Exception): pass
class RetrieveProxyException(Exception): pass

CMD_GET="""VERSION=MYPROXYv2
COMMAND=0
USERNAME=%s
PASSPHRASE=%s
LIFETIME=%d\0"""

class MyProxyServer(object):
    def __init__(self, hostname="localhost", port=7512):
        self.__hostname = hostname
        self.__port = port
        self.__username = ""
        self.__lifeTime = 43200
        self.__outputFilename = ""
        self.__keyType = crypto.TYPE_RSA
        self.__bits = 1024
        self.__messageDigest = "md5"
        self.__debugOutput = None
        
    def debugOutput(self, msg):
        if self.__debugOutput!=None:
            self.__debugOutput(msg)
        else:
            print msg
        
    def createCertRequest(self):
        """
        Create certificate request.
        
        Returns: certificate request PEM text, private key PEM text
        """
                        
        # Create certificate request
        
        req = crypto.X509Req()
    
        # Generate private key
        
        pkey = crypto.PKey()
        pkey.generate_key(self.__keyType, self.__bits)
    
        req.set_pubkey(pkey)
        req.sign(pkey, self.__messageDigest)
        
        return (crypto.dump_certificate_request(crypto.FILETYPE_ASN1,req),
               crypto.dump_privatekey(crypto.FILETYPE_PEM,pkey))
        
    def __deserializeResponse(self, msg):
        """
        Deserialize a MyProxy server response
        
        Returns: integer response, errortext (if any)
        """
        
        lines = msg.split('\n')
        
        # get response value
        
        responselines = filter( lambda x: x.startswith('RESPONSE'), lines)
        responseline = responselines[0]
        response = int(responseline.split('=')[1])
        
        # get error text
        
        errortext = ""
        errorlines = filter( lambda x: x.startswith('ERROR'), lines)
        for e in errorlines:
            etext = e.split('=')[1]
            errortext += etext
        
        return response,errortext
    
    def __deserializeCerts(self, inp_dat):
        
        pem_certs = []
        
        dat = inp_dat
        
        import base64
        while dat:
    
            # find start of cert, get length
            
            ind = dat.find('\x30\x82')
            if ind < 0:
                break
                
            len = 256*ord(dat[ind+2]) + ord(dat[ind+3])
    
            # extract der-format cert, and convert to pem
            
            c = dat[ind:ind+len+4]
            x509 = crypto.load_certificate(crypto.FILETYPE_ASN1,c)
            pem_cert = crypto.dump_certificate(crypto.FILETYPE_PEM,x509)
            pem_certs.append(pem_cert)
    
            # trim cert from data
            
            dat = dat[ind + len + 4:]
    
        return pem_certs
    
    def retrieveProxy(self,passphrase):
        """
        Function to retrieve a proxy credential from a MyProxy server
        
        Exceptions:  GetException, RetrieveProxyException
        """
        
        context = SSL.Context(SSL.SSLv3_METHOD)
        
        # disable for compatibility with myproxy server (er, globus)
        # globus doesn't handle this case, apparently, and instead
        # chokes in proxy delegation code
        
        context.set_options(0x00000800L)
        
        # connect to myproxy server
        
        self.debugOutput("debug: connect to myproxy server")
        conn = SSL.Connection(context,socket.socket())
        conn.connect((self.__hostname,self.__port))
        
        # send globus compatibility stuff
        
        self.debugOutput("debug: send globus compat byte")
        conn.write('0')
    
        # send get command
        
        self.debugOutput("debug: send get command")
        cmd_get = CMD_GET % (self.__username, passphrase, self.__lifeTime)
        conn.write(cmd_get)
    
        # process server response
        
        self.debugOutput("debug: get server response")
        dat = conn.recv(8192)
        self.debugOutput(dat)
        response,errortext = self.__deserializeResponse(dat)
        if response:
            raise GetException(errortext)
        else:
            self.debugOutput("debug: server response ok")
        
        # generate and send certificate request
        # - The client will generate a public/private key pair and send a 
        #   NULL-terminated PKCS#10 certificate request to the server.
        
        self.debugOutput("debug: send cert request")
        certreq,privatekey = self.createCertRequest()
        conn.send(certreq)
    
        # process certificates
        # - 1 byte , number of certs
        
        dat = conn.recv(1)
        numcerts = ord(dat[0])
        
        # - n certs
        
        self.debugOutput("debug: receive certs")
        dat = conn.recv(8192)
        
        #if debuglevel(2):
        #    print "debug: dumping cert data to myproxy.dump"
        #    f = file('myproxy.dump','w')
        #    f.write(dat)
        #    f.close()
    
        # process server response
        
        self.debugOutput("debug: get server response")
        resp = conn.recv(8192)
        response,errortext = self.__deserializeResponse(resp)
        if response:
            raise RetrieveProxyException(errortext)
        else:
            self.debugOutput("debug: server response ok")
    
        # deserialize certs from received cert data
        
        pem_certs = self.__deserializeCerts(dat)
        if len(pem_certs) != numcerts:
            self.debugOutput("Warning: %d certs expected, %d received" % (numcerts,len(pem_certs)))
    
        # write certs and private key to file
        # - proxy cert
        # - private key
        # - rest of cert chain
        
        self.debugOutput("debug: write proxy and certs to "+self.__outputFilename)
        f = file(self.__outputFilename,'w')
        f.write(pem_certs[0])
        f.write(privatekey)
        for c in pem_certs[1:]:
            f.write(c)
        f.close()
                
    def getHostname(self):
        return self.__hostname
    
    def setHostname(self, hostname):
        self.__hostname = hostname
        
    def getPort(self):
        return self.__port
    
    def setPort(self, port):
        self.__port = port
        
    def getUsername(self):
        return self.__username
    
    def setUsername(self, username):
        self.__username = username
        
    def getLifeTime(self):
        return self.__lifeTime
        
    def setLifeTime(self, lifeTime):
        self.__lifeTime = lifeTime
        
    def getOutputFilename(self):
        return self.__outputFilename
    
    def setOutputFilename(self, filename):
        self.__outputFilename = filename
        
    def getKeyType(self):
        return self.__keyType
    
    def setKeyType(self, keyType):
        self.__keyType = keyType
        
    def getBits(self):
        return self.__bits
    
    def setBits(self, bits):
        self.__bits = bits
        
    def getMessageDigest(self):
        return self.__messageDigest
    
    def setMessageDigest(self, digest):
        self.__messageDigest = digest
    
    hostname = property(getHostname, setHostname)
    port = property(getPort, setPort)
    username = property(getUsername, setUsername)
    lifeTime = property(getLifeTime, setLifeTime)
    outputFilename = property(getOutputFilename, setOutputFilename)
    keyType = property(getKeyType, setKeyType)
    bits = property(getBits, setBits)
    messageDigest = property(getMessageDigest, setMessageDigest)
    
if __name__ == '__main__':
    import sys
    import optparse
    import getpass
    
    parser = optparse.OptionParser()
    parser.add_option("-s", "--pshost", dest="host", 
                       help="The hostname of the MyProxy server to contact")
    parser.add_option("-p", "--psport", dest="port", default=7512,
                       help="The port of the MyProxy server to contact")
    parser.add_option("-l", "--username", dest="username", 
                       help="The username with which the credential is stored on the MyProxy server")
    parser.add_option("-o", "--out", dest="outfile", 
                       help="The username with which the credential is stored on the MyProxy server")
    parser.add_option("-t", "--proxy-lifetime", dest="lifetime", default=43200,
                       help="The username with which the credential is stored on the MyProxy server")
    parser.add_option("-d", "--debug", dest="debug", default=0,
                       help="Debug mode: 1=print debug info ; 2=print as in (1), and dump data to myproxy.dump")

    (options,args) = parser.parse_args()
    
    debug = options.debug

    # process options
    host = options.host
    if not host:
        print "Error: MyProxy host not specified"
        sys.exit(1)
    port = int(options.port)
    username = options.username
    if not username:
        if sys.platform == 'win32':
            username = os.environ["USERNAME"]
        else:
            import pwd
            username = pwd.getpwuid(os.geteuid())[0]
    lifetime = int(options.lifetime)
    
    outfile = options.outfile
    if not outfile:
        if sys.platform == 'win32':
            outfile = 'proxy'
        elif sys.platform in ['linux2','darwin']:
            outfile = '/tmp/x509up_u%s' % (os.getuid())
            
    myProxyServer = MyProxyServer(host, port)
    myProxyServer.username = username
    myProxyServer.lifeTime = lifetime
    myProxyServer.outputFilename = outfile

    # Get MyProxy password
    passphrase = getpass.getpass()
        
    try:
        myProxyServer.retrieveProxy(passphrase)
        print "A proxy has been received for user %s in %s." % (myProxyServer.username, myProxyServer.outputFilename)
    except Exception, e:
        print "Error:", e
    
