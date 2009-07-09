#
# UserPrefsPage
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

"""UserPrefsPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

import arc

class UserPrefsPage(ApplicationSecurePage):
    """Page for displaying user preferences settings.
    
    Currently this page only handles the users default email, but will
    probarbly handle more as the portal functionality grows."""
    
    def onInitPage(self):
        tabControl = Web.Ui.jQueryTabs(self)
        tabControl.name = "tabs"
        self.addControl(tabControl)    
    
    def title(self):
        """Return page title."""
        return 'User preferences'
    
    def writeContent(self):
        """Render page HTML."""
        if self.session().hasValue("userprefs_status"):

            # Show any form message boxes
            
            if self.session().value("userprefs_status")<>"":
                Web.Dialogs.messageBox(self, self.session().value("userprefs_status"), "Message", "SecureWelcomePage", width="25em")

            self.session().delValue("userprefs_status")
        
        else:
            
            # Retrieve user settings
            
            user = Lap.Session.User(self.session().value('authenticated_user'))
            
            # Create preferences form
            
            adapterName = self.request().adapterName()  
            
            form = Web.Ui.Form("userPrefsPage", "%s/context/UserPrefsPage" % adapterName, "User preferences", "35em")
            form.setDefaultLabelWidth("12em")
            
            form.beginFieldSet("General", tabName="tab3")
            form.addText("Submit timeout (s)", "timeout", self.timeout, "10em", fieldType="int")
            form.addBreak()
            form.addText("Default broker", "broker", self.broker, "10em", fieldType="string")
            form.endFieldSet()                        
            
            form.beginFieldSet("Preferred clusters", tabName="tab1")
            form.beginSelect("Clusters", "preferredClusters", size=5, width="20em", labelWidth="8em")
            for cluster in self.preferredClusters:
                form.addOption(cluster)
            form.endSelect()
            form.addText("Cluster", "preferredCluster", "", fieldType="hostname", width="20em", labelWidth="8em")
            form.addBreak()
            form.beginIndent("9em")
            form.addSubmitButton("Add", "_action_addPreferredCluster")
            form.addSubmitButton("Clear", "_action_clearPreferredClusters")
            form.addSubmitButton("Remove", "_action_removePreferredCluster")
            form.endIndent()
            form.endFieldSet()

            form.beginFieldSet("Rejected clusters", tabName="tab2")
            form.beginSelect("Clusters2", "rejectedClusters", size=5, width="20em", labelWidth="8em")
            for cluster in self.rejectedClusters:
                form.addOption(cluster)
            form.endSelect()
            form.addText("Cluster", "rejectedCluster", "", fieldType="hostname", width="20em", labelWidth="8em")
            form.addBreak()
            form.beginIndent("9em")
            form.addSubmitButton("Add", "_action_addRejectedCluster")
            form.addSubmitButton("Clear", "_action_clearRejectedClusters")
            form.addSubmitButton("Remove", "_action_removeRejectedCluster")
            form.endIndent()
            form.endFieldSet()
                            
            form.addFormButton("Save", "_action_saveSettings")
            form.addFormButton("Cancel", "_action_cancelDialog")
            
            form.setHaveSubmit(False)
            
            form.render(self)
        
    def setFormStatus(self, status):
        """Set the form status text.
        
        If not empty the status text will be displayed in dialog box."""
        self.session().setValue("userprefs_status", status)
        
    def addPreferredCluster(self):
        """
        Add cluster to preferred clusters.
        """
        
        cluster = self.getRawString(self.request(), "preferredCluster")
        
        if cluster != None:
            self.preferredClusters.append(cluster)
            
        self.writeBody()
            
    def removePreferredCluster(self):
        """
        Remove cluster from preferred cluster listbox.
        """
        selectedCluster = self.getRawString(self.request(), "preferredClusters")
        
        if selectedCluster != None:
            try:
                self.preferredClusters.remove(selectedCluster)
            except:
                pass
                        
        self.writeBody()
    
    def clearPreferredClusters(self):
        """
        Clear preferred cluster listbox.
        """
        
        self.preferredClusters[:] = []
        self.writeBody()

        
    def addRejectedCluster(self):
        """
        Add cluster to rejected clusters.
        """
        
        cluster = self.getRawString(self.request(), "rejectedCluster")
        
        if cluster != None:
            self.rejectedClusters.append(cluster)
            
        self.writeBody()
            
    def removeRejectedCluster(self):
        """
        Remove cluster from rejected cluster listbox.
        """
        selectedCluster = self.getRawString(self.request(), "rejectedClusters")
        
        if selectedCluster != None:
            try:
                self.rejectedClusters.remove(selectedCluster)
            except:
                pass
                        
        self.writeBody()
    
    def clearRejectedClusters(self):
        """
        Clear rejected cluster listbox.
        """
        
        self.rejectedClusters[:] = []
        self.writeBody()

    def saveSettings(self):
        """Save settings (action)
        
        Saves the user preferences in the portal user directory.
        """
                
        # Add services from dialog string list
        
        preferredClusters = arc.XMLNode(arc.NS(), "PreferredClusters")
        
        for preferredCluster in self.preferredClusters:
            urlTag = preferredClusters.NewChild("URL")
            urlTag.NewAttribute("Flavour").Set("ARC0")
            urlTag.NewAttribute("ServiceType").Set("cluster")    
            urlTag.Set(str(preferredCluster))
            
        rejectedClusters = arc.XMLNode(arc.NS(), "RejectedClusters")

        for rejectedCluster in self.rejectedClusters:
            urlTag = rejectedClusters.NewChild("URL")
            urlTag.NewAttribute("Flavour").Set("ARC0")
            urlTag.NewAttribute("ServiceType").Set("cluster")    
            urlTag.Set(str(rejectedCluster))
            
        if self.arcClient.userConfig.ConfTree().Get("PreferredClusters")!="":
            self.arcClient.userConfig.ConfTree().Get("PreferredClusters").Replace(preferredClusters)
        else:
            self.arcClient.userConfig.ConfTree().NewChild(preferredClusters)
           
        if self.arcClient.userConfig.ConfTree().Get("RejectedClusters")!="":
            self.arcClient.userConfig.ConfTree().Get("RejectedClusters").Replace(rejectedClusters)
        else:
            self.arcClient.userConfig.ConfTree().NewChild(rejectedClusters)
            
        timeout = self.getInt(self.request(), "timeout")
        broker = self.getString(self.request(), "broker")
        
        if timeout!=None:
            self.timeout = timeout
            self.arcClient.userConfig.SetTimeOut(timeout)
        
        if broker!=None:
            self.broker = timeout
            self.arcClient.userConfig.SetBroker(broker)

        self.arcClient.saveConfiguration()

        self.setFormStatus("Settings have been saved.")

        self.session().delValue("userprefs_preferredclusters")
        self.session().delValue("userprefs_rejectedclusters")
        self.session().delValue("userprefs_timeout")
        self.session().delValue("userprefs_broker")

        self.writeBody()
        
    def cancelDialog(self):
        """Cancel dialog (action)
        
        Cancels the active input and returns to the welcome page (SecureWelcomePage)."""
        
        self.session().delValue("userprefs_preferredclusters")
        self.session().delValue("userprefs_rejectedclusters")
        self.session().delValue("userprefs_timeout")
        self.session().delValue("userprefs_broker")
        
        self.forward("SecureWelcomePage")
        
    def actions(self):
        """Return a list of implemented actions."""
        return ApplicationSecurePage.actions(self) + ["saveSettings", "cancelDialog",
                                                      "addPreferredCluster", "removePreferredCluster",
                                                      "clearPreferredClusters", "addRejectedCluster",
                                                      "removeRejectedCluster", "clearRejectedClusters"]
    
    def getPreferredClusters(self):
        """
        Return a list of preferred clusters.
        """
        if not self.session().hasValue("userprefs_preferredclusters"):
            preferredClusters = []

            config = self.arcClient.userConfig.ConfTree()
           
            preferredClustersNode = config.Get("PreferredClusters")
            
            for i in range(preferredClustersNode.Size()):
                preferredClusters.append(str(preferredClustersNode.Child(i)))
            
            self.session().setValue("userprefs_preferredclusters", preferredClusters)
            return preferredClusters
        else:
            return self.session().value("userprefs_preferredclusters")
        
    def getRejectedClusters(self):
        if not self.session().hasValue("userprefs_rejectedclusters"):
            rejectedClusters = []

            config = self.arcClient.userConfig.ConfTree()
           
            rejectedClustersNode = config.Get("RejectedClusters")
            for i in range(rejectedClustersNode.Size()):
                rejectedClusters.append(str(rejectedClustersNode.Child(i)))
            
            self.session().setValue("userprefs_rejectedclusters", rejectedClusters)
            return rejectedClusters
        else:
            return self.session().value("userprefs_rejectedclusters")
            
    def getTimeout(self):
        if not self.session().hasValue("userprefs_timeout"):
            timeoutValue = self.arcClient.userConfig.ConfTree().Get("TimeOut")
            if timeoutValue!="":
                self.session().setValue("userprefs_timeout", str(timeoutValue))
            else:
                self.session().setValue("userprefs_timeout", str(20))
        
        return self.session().value("userprefs_timeout")
            
    def setTimeout(self, timeout):
        self.session().setValue("userprefs_timeout", str(timeout))

    def getBroker(self):
        if not self.session().hasValue("userprefs_broker"):
            brokerValue = self.arcClient.userConfig.ConfTree().Get("Broker")
            if brokerValue!="":
                self.session().setValue("userprefs_broker", str(brokerValue))
            else:
                self.session().setValue("userprefs_broker", "RandomBroker")

        return self.session().value("userprefs_broker")
            
    def setBroker(self, broker):
        self.session().setValue("userprefs_broker", str(broker))

    preferredClusters = property(getPreferredClusters)
    rejectedClusters = property(getRejectedClusters)
    timeout = property(getTimeout, setTimeout)
    broker = property(getBroker, setBroker)
    
