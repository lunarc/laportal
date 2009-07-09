#
# UploadProxyPage base class module
#
# Copyright (C) 2006-2009 Jonas Lindemann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""UploadProxyPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from time import *

import os, sys, stat, pwd, string, pickle

from Grid.Clients import ArcClient

import Lap
import Lap.Session
from Lap.Log import *

import Web
import Web.Ui
import Web.Dialogs

class UploadProxyPage(ApplicationSecurePage):
    """Base class for job plugins
    
    This class provides all the neccesary functions for editing
    job definitions."""
    
    # ----------------------------------------------------------------------
    # Private methods
    # ----------------------------------------------------------------------    

    def _uploadFile(self, fieldName, destDir, newFilename=""):
        """Handles a HTTP file upload request from the
        request file, fieldName, and copies it to the directory
        specified by destDir."""
        if self.request().hasField(fieldName):

            filename = ""

            ok = True
            try:
                f = self.request().field(fieldName)
                fileContent = f.file.read()
                
                
                if f.filename.find("\\")!=-1:
                    lapDebug("Explorer upload...")
                    
                    lastBackslash = f.filename.rfind("\\")
                    filename = f.filename[lastBackslash+1:]
                    lapDebug("modified filename = " + filename)
                else:
                    filename = f.filename
                    
                lapDebug("Upload filename = " + filename)
                
                if newFilename=="":                
                    inputFile = file(os.path.join(destDir, filename), "w")
                    inputFile.write(fileContent)
                    inputFile.close()
                    os.chmod(os.path.join(destDir,newFilename), 0600)                    
                else:
                    inputFile = file(os.path.join(destDir, newFilename), "w")
                    inputFile.write(fileContent)
                    inputFile.close()
                    os.chmod(os.path.join(destDir,filename), 0600)                    
                    
            except:
                ok = False
                pass
            
            if ok:
                lapInfo("File, %s, uploaded to %s." % (filename, destDir))
                return ok, filename
            else:
                return ok, ""
            
        else:
            return False, ""
        
    def title(self):
        """Return title of the page."""
        return 'Grid preferences'
    
    def writeContent(self):
        """Render the grid preferences page."""
        
        if self.session().hasValue("proxyupload_status"):

            # Show any form message boxes
            
            if self.session().value("proxyupload_status")<>"":
                Web.Dialogs.messageBox(self, self.session().value("proxyupload_status"), "Message", "SecureWelcomePage", width="25em")

            self.session().delValue("proxyupload_status")
        
        else:
            
            # Retrieve user settings
            
            user = Lap.Session.User(self.session().value('authenticated_user'))
                                    
            # Create preferences form
            
            adapterName = self.request().adapterName()          
            form = Web.Ui.Form("uploadProxyPage", "%s/context/UploadProxyPage" % adapterName, "Upload proxy", "25em")
                            
            form.setDefaultLabelWidth("10.0em")
            
            form.addFile("Proxy file","proxyUploadFilename")
                        
            form.addFormButton("Upload", "_action_uploadProxy")
                    
            form.render(self)
            
    def uploadProxy(self):
        if self.session().hasValue("authenticated_user"):
            user = Lap.Session.User(self.session().value('authenticated_user'))
            self._uploadFile("proxyUploadFilename", user.homeDir, "proxy.pem")
            
            proxyFilename = os.path.join(user.homeDir, "proxy.pem")
            os.chmod(proxyFilename, 0600)
            
            client = self.arcClient
            client.proxyFilename = proxyFilename
        
            
            if client.hasValidProxy():
                self.setFormStatus("Proxy uploaded succesfully.")
            else:
                self.setFormStatus("File uploaded, but not valid proxy.")
        else:
            self.setFormStatus("Proxy upload failed.")
            
        self.writeBody()
        
    def setFormStatus(self, status):
        """Set the text to be displayed in the form status box."""
        
        self.session().setValue("proxyupload_status", status)
        
    def actions(self):
        """Return a list of actions used on this page."""
        
        return ApplicationSecurePage.actions(self) + ["uploadProxy"]

        
