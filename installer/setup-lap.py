#!/bin/env python

import os, string, sys

class Package:
    def __init__(self):
        self._targetDir = "./opt"
        self._version = "1.0"
        self._downloadURL = ""
        self._fileList = []
        self._extractTool = "tar"
        self._packageDir = "./packages"
        
    def setTargetDir(self, targetDir):
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
                os.system("wget -q -P " + self._packageDir+ " " + url)
                print "\t\t[Downloaded]"
            else:
                print "\t\t[Exists]"
                
    def extract(self):
        for filename in self._fileList:
            realFilename = filename % self._version
            os.system("tar xzf %s -C %s" % (os.path.join(self._packageDir, realFilename), self._targetDir))
            
    def getInstallDir(self, idx):
        if idx>=0 and idx<len(self._fileList):
            realFilename = self._fileList[idx] % self._version
            packageDir, ext = os.path.splitext(realFilename)
            packageDir, ext = os.path.splitext(packageDir)
            packageDir = os.path.join(self._targetDir, packageDir)
            return packageDir
        else:
            return ""
    
    def setup(self):
        pass
    
class WebWare(Package):
    def __init__(self):
        Package.__init__(self)
        self.setVersion("0.9.2")
        self.setDownloadURL("http://heanet.dl.sourceforge.net/sourceforge/webware")
        self.addFile("Webware-%s.tar.gz")
            
    def setup(self):
        realFilename = self._fileList[0] % self._version
        packageDir, ext = os.path.splitext(realFilename)
        packageDir, ext = os.path.splitext(packageDir)
        packageDir = os.path.join(self._targetDir, packageDir)
        print packageDir
        if os.path.exists(packageDir):
            currDir = os.getcwd()
            os.chdir(packageDir)
            os.system("python ./install.py")
            
class AppPortal(Package):
    def __init__(self):
        Package.__init__(self)
        self._webwareDir = ""
        self._appDir = "/opt/lap"
        self.setVersion("0.8.0-20061018")
        self.setDownloadURL("http://grid.lunarc.lu.se/lapsrc")
        self.addFile("lap-config-%s.tar.gz")
        self.addFile("lap-layout-%s.tar.gz")
        self.addFile("lap-plugins-%s.tar.gz")
        self.addFile("lap-source-%s.tar.gz")
        
    def setApplicationDir(self, appDir):
        self._appDir = appDir
        
    def setWebwareDir(self, webwareDir):
        self._webwareDir = webwareDir      

webware = WebWare()
print "Downloading WebWare..."
webware.download()
print "Extracting WebWare..."
webware.extract()
print "Setting up WebWare..."
#webware.setup()

webwareInstallDir = webware.getInstallDir(0)
print "Webware installed at: ", webwareInstallDir

portal = AppPortal()
print "Downloading portal..."
portal.download()
