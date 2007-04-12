from Web.ApplicationPage import ApplicationPage
from MiscUtils.Funcs import uniqueId
import string, types

import Web.Dialogs

class LogoutPage(ApplicationPage):
	def title(self):
		return 'Log Out'

	def writeContent(self):

		adapterName = self.request().adapterName()		
		self.session().invalidate()
		Web.Dialogs.messageBox(self, "You have been logged out.", "Information", "%s/context/WelcomePage" % adapterName)

