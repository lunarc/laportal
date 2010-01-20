#
# UploadProxyPage base class module
#
# Copyright (C) 2006-2010 Jonas Lindemann
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

from Grid.MyProxy import *

class MyProxyPage(ApplicationSecurePage):
    """Base class for job plugins
    
    This class provides all the neccesary functions for editing
    job definitions."""
    
    # ----------------------------------------------------------------------
    # Private methods
    # ----------------------------------------------------------------------    
        
    def title(self):
        """Return title of the page."""
        return 'Grid preferences'
    
    def onInitPage(self):
        ApplicationSecurePage.onInitPage(self)

        adapterName = self.request().adapterName()          
        
        self.__form = Web.Ui.Form("retrieveProxyForm", "%s/context/MyProxyPage" % adapterName, "Retrieve proxy", "25em")
                        
        self.__form.setDefaultLabelWidth("10.0em")
        self.__form.addText("MyProxy server", "proxyServer", fieldType = "hostname")
        self.__form.addText("User", "proxyUsername", fieldType = "string")
        self.__form.addPassword("Passphrase", "proxyPassphrase", fieldType = "password")
                    
        self.__form.addFormButton("Retrieve", "_action_retrieveProxy")
        self.__form.setHaveSubmit(False)
    
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

            self.__form.render(self)
            
    def retrieveProxy(self):
        if self.session().hasValue("authenticated_user"):
            user = Lap.Session.User(self.session().value('authenticated_user'))
            
            if self.session().hasValue("myproxyForm"):
                
                # Get values from form

                values = self.__form.retrieveFieldValues(self.request())
                
                # Query proxyServer
                
                proxyFilename = os.path.join(user.homeDir, "proxy.pem")
                
                proxyServer = MyProxyServer(values["proxyServer"])
                proxyServer.username = values["proxyUsername"]
                proxyServer.outputFilename = proxyFilename
                
                try:
                    proxyServer.retrieveProxy(values["proxyPassphrase"])
                    os.chmod(proxyFilename, 0600)               
                    self.setFormStatus("A proxy has been received for user %s." % (proxyServer.username))
                except Exception, e:
                    self.setFormStatus("Error:"+str(e))
            else:
                self.setFormStatus("Could not load form.")
        else:
            self.setFormStatus("Not authenticated.")
            
        self.writeBody()
        
    def setFormStatus(self, status):
        """Set the text to be displayed in the form status box."""
        
        self.session().setValue("proxyupload_status", status)
        
    def actions(self):
        """Return a list of actions used on this page."""
        
        return ApplicationSecurePage.actions(self) + ["retrieveProxy"]

        
