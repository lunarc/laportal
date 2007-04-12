from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

class UserPrefsPage(ApplicationSecurePage):
	
	def title(self):
		return 'User preferences'
	
	def writeContent(self):
		
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
		self.session().setValue("userprefs_status", status)		
		
	def saveSettings(self):
		
		# Retrieve user settings
		
		user = Lap.Session.User(self.session().value('authenticated_user'))
		
		defaultEmail = self.getEmail(self.request(), "defaultEmail")

		if defaultEmail != None:
			user.setDefaultMail(defaultEmail)
	
		user.savePrefs()
		
		self.setFormStatus("Settings have been saved.")
		self.writeBody()
		
	def cancelDialog(self):
		self.forward("SecureWelcomePage")
		
	def actions(self):
		return ApplicationSecurePage.actions(self) + ["saveSettings", "cancelDialog"]
	
