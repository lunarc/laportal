from Web.ApplicationPage import ApplicationPage

from MiscUtils.Funcs import uniqueId
import string, types

import Web.Dialogs
import Web.Ui

class LoginPage(ApplicationPage):
	def title(self):
		return 'Log In'

	def htBodyArgs(self):
		return ApplicationPage.htBodyArgs(self) + ' onload="document.loginform.password.focus();"' % locals()

	def writeContent(self):

		# Any messages to display ? 		

		extra = self.request().field('extra', None)
		
		if not extra and self.request().isSessionExpired() and not self.request().hasField('logout'):
			extra = 'You have been automatically logged out due to inactivity.'
		
		if extra:
			Web.Dialogs.messageBox(self, self.htmlEncode(extra))
			self.writeln("<br>")
			self.writeln("<br>")

		# Create unique loginid			
		
		loginid = uniqueId(self)
		self.session().setValue('loginid', loginid)

		action = self.request().field('action', '')
		
		# Create login form		

		form = Web.Ui.Form("loginform", action, "Login", "30em")

		form.addBreak()
		form.addFile("Proxy file", "proxy", "", "16em")
		form.addHidden("", "loginid", loginid)
		form.setAction(action)
		form.addBreak()
		form.setSubmitButton("login", "Login")

		# Forward any passed in values to the user's intended page after successful login,
		# except for the special values used by the login mechanism itself
		
		for name, value in self.request().fields().items():
			if name not in 'login loginid proxy extra logout'.split():
				if isinstance(value, types.ListType):
					for valueStr in value:
						form.addHidden("", name, valueStr)
				else:
					form.addHidden("", name, value)

		form.render(self)
