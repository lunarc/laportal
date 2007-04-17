#
# GridPrefsPage
#
# Copyright (C) 2006-2007 Jonas Lindemann
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

class GridPrefsPage(ApplicationSecurePage):
	"""Grid preferences dialog page class."""
	
	def title(self):
		"""Return title of the page."""
		return 'Grid preferences'
	
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
			
			preferredClusters = []
			rejectedClusters = []
			submitTimeout = 120
			
			# Store the settings in session variables, enabling
			# the user to cancel the dialog without saving any changes.
			
			if self.session().hasValue("gridprefs_preferredClusters"):
				preferredClusters = self.session().value("gridprefs_preferredClusters")
				rejectedClusters = self.session().value("gridprefs_rejectedClusters")
			else:
				preferredClusters = user.getPreferredClusters()
				rejectedClusters = user.getRejectedClusters()
				self.session().setValue("gridprefs_preferredClusters", preferredClusters)
				self.session().setValue("gridprefs_rejectedClusters", rejectedClusters)
				
			if self.session().hasValue("gridprefs_queryTimeout"):
				submitTimeout = self.session().value("gridprefs_queryTimeout")
			else:
				submitTimeout = user.getSubmitTimeout()
				self.session().setValue("gridprefs_submitTimeout", submitTimeout)
			
			# Create preferences form
			
			adapterName = self.request().adapterName()	
			
			form = Web.Ui.Form("gridPrefsPage", "%s/context/GridPrefsPage" % adapterName, "Grid preferences", "25em")
			
			form.setDefaultLabelWidth("10.0em")
			
			form.beginFieldSet("Preferred clusters")
			form.beginSelect("Clusters", "preferredClusters", size=5, width="12em")
			for cluster in preferredClusters:
				form.addOption(cluster)
			form.endSelect()
			form.addText("Cluster", "preferredCluster", "", fieldType="hostname", width="11em")
			form.addBreak()
			form.beginIndent("11em")
			form.addSubmitButton("Add", "_action_addPreferredCluster")
			form.addSubmitButton("Clear", "_action_clearPreferredClusters")
			form.addSubmitButton("Remove", "_action_removePreferredCluster")
			form.endIndent()
			form.endFieldSet()

			form.beginFieldSet("Rejected clusters")
			form.beginSelect("Clusters", "rejectedClusters", size=5, width="12em")
			for cluster in rejectedClusters:
				form.addOption(cluster)
			form.endSelect()
			form.addText("Cluster", "rejectedCluster", "", fieldType="hostname", width="11em")
			form.addBreak()
			form.beginIndent("11em")
			form.addSubmitButton("Add", "_action_addRejectedCluster")
			form.addSubmitButton("Clear", "_action_clearRejectedClusters")
			form.addSubmitButton("Remove", "_action_removeRejectedCluster")
			form.endIndent()
			form.endFieldSet()

			form.beginFieldSet("Miscellaneous")
			form.addText("Submit timeout (s)", "submitTimeout", submitTimeout, "5em", fieldType="int")
			form.endFieldSet()
			
			form.addFormButton("Save", "_action_saveSettings")
			form.addFormButton("Cancel", "_action_cancelDialog")
			
			form.setHaveSubmit(False)
			
			form.render(self)
		
	def setFormStatus(self, status):
		"""Set the text to be displayed in the form status box."""
		
		self.session().setValue("gridprefs_status", status)
		
	def addPreferredCluster(self):
		"""Add cluster to preferred cluster listbox."""
		
		cluster = self.getHostname(self.request(), "preferredCluster")
		preferredClusters = self.session().value("gridprefs_preferredClusters")
		
		if cluster != None:
			preferredClusters.append(cluster)
			
		self.writeBody()
			
	def removePreferredCluster(self):
		"""Remove cluster from preferred cluster listbox."""
		
		preferredClusters = self.session().value("gridprefs_preferredClusters")
		selectedCluster = self.getHostname(self.request(), "preferredClusters")
		
		if selectedCluster != None:
			for i in range(len(preferredClusters)):
				if preferredClusters[i] == selectedCluster:
					del preferredClusters[i]
					break
			
		self.writeBody()
	
	def clearPreferredClusters(self):
		"""Clear preferred cluster listbox."""
		
		cluster = self.getHostname(self.request(), "preferredCluster")
		preferredClusters = self.session().value("gridprefs_preferredClusters")
		
		del preferredClusters[0:len(preferredClusters)]
			
		self.writeBody()
		
	def addRejectedCluster(self):
		"""Add cluster to rejected cluster listbox."""
		
		cluster = self.getHostname(self.request(), "rejectedCluster")
		rejectedClusters = self.session().value("gridprefs_rejectedClusters")
		
		print cluster
		
		if cluster != None:
			rejectedClusters.append(cluster)
			
		self.writeBody()
	
	def removeRejectedCluster(self):
		"""Remove cluster from rejected cluster listbox."""
		
		rejectedClusters = self.session().value("gridprefs_rejectedClusters")
		selectedCluster = self.getHostname(self.request(), "rejectedClusters")
		
		if selectedCluster != None:
			for i in range(len(rejectedClusters)):
				if rejectedClusters[i] == selectedCluster:
					del rejectedClusters[i]
					break
			
		self.writeBody()
	
	def clearRejectedClusters(self):
		"""Clear preferred cluster listbox."""
		
		cluster = self.getHostname(self.request(), "rejectedCluster")
		rejectedClusters = self.session().value("gridprefs_rejectedClusters")

		del rejectedClusters[0:len(rejectedClusters)]
			
		self.writeBody()

	def saveSettings(self):
		"""Save user settings to disk (user.prefs)."""
		
		# Retrieve user settings
		
		user = Lap.Session.User(self.session().value('authenticated_user'))
		
		preferredClusters = self.session().value("gridprefs_preferredClusters")
		rejectedClusters = self.session().value("gridprefs_rejectedClusters")
		
		user.assignPreferredClusters(preferredClusters)
		user.assignRejectedClusters(rejectedClusters)
		
		submitTimeout = self.getInt(self.request(), "submitTimeout")
		if submitTimeout!=None:
			user.setSubmitTimeout(submitTimeout)
		
		user.savePrefs()
		
		self.session().delValue("gridprefs_preferredClusters")
		self.session().delValue("gridprefs_rejectedClusters")
		self.session().delValue("gridprefs_submitTimeout")
		
		self.setFormStatus("Settings have been saved.")
		self.writeBody()
		
	def cancelDialog(self):
		"""Cancel grid preferences dialog witouth saving changes."""
		
		self.session().delValue("gridprefs_preferredClusters")
		self.session().delValue("gridprefs_rejectedClusters")
		self.session().delValue("gridprefs_submitTimeout")		
		self.forward("SecureWelcomePage")
		
	def actions(self):
		"""Return a list of actions used on this page."""
		
		return ApplicationSecurePage.actions(self) + ["saveSettings", "cancelDialog",
							      "addPreferredCluster", "clearPreferredClusters",
							      "removePreferredCluster", "addRejectedCluster",
							      "removeRejectedCluster", "clearRejectedClusters"]
	
