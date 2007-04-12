from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs

class LoginPageDummy(ApplicationSecurePage):

	def title(self):
		return 'Logged in'

	def writeContent(self):
		
		adapterName = self.request().adapterName()		
		
		Web.Dialogs.messageBox(self, "You have been logged in.", "Information", "%s/context/SecureWelcomePage" % adapterName)

				

