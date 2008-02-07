#
# UserPrefsPage
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

"""UserPrefsPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

class UserPrefsPage(ApplicationSecurePage):
	"""Page for displaying user preferences settings.
	
	Currently this page only handles the users default email, but will
	probarbly handle more as the portal functionality grows."""
	
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
	
			form.addText("Default email", "defaultEmail", user.getDefaultMail(), "16em", "20em")
			
			form.addFormButton("Save", "_action_saveSettings")
			form.addFormButton("Cancel", "_action_cancelDialog")
			
			form.setHaveSubmit(False)
			
			form.render(self)
		
	def setFormStatus(self, status):
		"""Set the form status text.
		
		If not empty the status text will be displayed in dialog box."""
		self.session().setValue("userprefs_status", status)		
		
	def saveSettings(self):
		"""Save settings (action)
		
		Saves the user preferences in the portal user directory."""
		# Retrieve user settings
		
		user = Lap.Session.User(self.session().value('authenticated_user'))
		
		defaultEmail = self.getEmail(self.request(), "defaultEmail")

		if defaultEmail != None:
			user.setDefaultMail(defaultEmail)
	
		user.savePrefs()
		
		self.setFormStatus("Settings have been saved.")
		self.writeBody()
		
	def cancelDialog(self):
		"""Cancel dialog (action)
		
		Cancels the active input and returns to the welcome page (SecureWelcomePage)."""
		self.forward("SecureWelcomePage")
		
	def actions(self):
		"""Return a list of implemented actions."""
		return ApplicationSecurePage.actions(self) + ["saveSettings", "cancelDialog"]
	
