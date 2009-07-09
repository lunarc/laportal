#
# GridPrefsPage
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

"""GridPrefsPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

import arc

class GridPrefsPage(ApplicationSecurePage):
    """Grid preferences dialog page class."""
    
    def title(self):
        """Return title of the page."""
        return 'Grid preferences'
    
    #def onInitPage(self):
    #    tabControl = Web.Ui.jQueryTabs(self)
    #    tabControl.name = "tabs"
    #   self.addControl(tabControl)
    
    def writeContent(self):
        """Render the grid preferences page."""
        
        if self.session().hasValue("gridprefs_status"):

            # Show any form message boxes
            
            if self.session().value("gridprefs_status")<>"":
                Web.Dialogs.messageBox(self, self.session().value("gridprefs_status"), "Message", "SecureWelcomePage", width="25em")

            self.session().delValue("gridprefs_status")
        
        else:
            
            # Retrieve user settings
            
            user = Lap.Session.User(self.session().value('authenticated_user'))
                                                
            # Create preferences form
            
            adapterName = self.request().adapterName()  
            
            form = Web.Ui.Form("gridPrefsPage", "%s/context/GridPrefsPage" % adapterName, "Grid preferences", "35em")
            form.tabbedForm = True
            
            form.setDefaultLabelWidth("10.0em")

            form.beginSelect("Default services", "defaultServices", size=5, width="25em")
            
            for service in self.defaultServices:
                form.addOption(service)
                
            form.endSelect()
            form.addBreak()
            form.addText("Service", "service", "", fieldType="hostname", width="30m")
            form.addBreak()
            form.beginIndent("11em")
            form.addSubmitButton("Add", "_action_addDefaultService")
            form.addSubmitButton("Clear", "_action_clearDefaultServices")
            form.addSubmitButton("Remove", "_action_removeDefaultService")
            form.endIndent()
            
            form.addFormButton("Save", "_action_saveSettings")
            form.addFormButton("Cancel", "_action_cancelDialog")
            
            form.setHaveSubmit(False)
            
            form.render(self)
        
    def setFormStatus(self, status):
        """Set the text to be displayed in the form status box."""
        
        self.session().setValue("gridprefs_status", status)
        
    def addDefaultService(self):
        """Add cluster to preferred cluster listbox."""
        
        service = self.getRawString(self.request(), "service")
        
        if service != None:
            self.defaultServices.append(service)
            
        self.writeBody()
            
    def removeDefaultService(self):
        """
        Remove cluster from preferred cluster listbox.
        """
        
        selectedService = self.getRawString(self.request(), "defaultServices")
        
        if selectedService != None:
            try:
                self.defaultServices.remove(selectedService)
            except:
                pass
                        
        self.writeBody()
    
    def clearDefaultServices(self):
        """
        Clear preferred cluster listbox.
        """
        
        self.defaultServices[:] = []
        self.writeBody()

    def saveSettings(self):
        """
        Save user settings to disk (user.prefs).
        """
        
        # Create a new "DefaultServices" XMLNode.
        
        newServices = arc.XMLNode(arc.NS(), "DefaultServices")
        
        # Add services from dialog string list
        
        services = self.arcClient.userConfig.ConfTree().Get("DefaultServices")
        for service in self.defaultServices:
            urlTag = newServices.NewChild("URL")
            urlTag.NewAttribute("Flavour").Set("ARC0")
            urlTag.NewAttribute("ServiceType").Set("index")    
            urlTag.Set(str(service))
            
        # Replace old services node with new one.
        
        self.arcClient.userConfig.ConfTree().Get("DefaultServices").Replace(newServices)
        self.arcClient.saveConfiguration()
        
        self.session().delValue("gridprefs_defaultservices")
        
        self.setFormStatus("Settings have been saved.")
        self.writeBody()
        
    def cancelDialog(self):
        """Cancel grid preferences dialog witouth saving changes."""
        
        self.session().delValue("gridprefs_defaultServices")
        self.forward("SecureWelcomePage")
        
    def actions(self):
        """Return a list of actions used on this page."""
        
        return ApplicationSecurePage.actions(self) + ["saveSettings", "cancelDialog",
                                  "addDefaultService", "clearDefaultServices",
                                  "removeDefaultService"]
        
    def getDefaultServices(self):
        if not self.session().hasValue("gridprefs_defaultservices"):
            defaultServices = []
            
            services = self.arcClient.userConfig.ConfTree().Get("DefaultServices")
            for i in range(services.Size()):
                defaultServices.append(str(services.Child(i)))
            
            self.session().setValue("gridprefs_defaultservices", defaultServices)
            return defaultServices
        else:
            return self.session().value("gridprefs_defaultservices")
        
    defaultServices = property(getDefaultServices)
    
