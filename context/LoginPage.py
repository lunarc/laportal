#
# LoginPage
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

"""LogoutPage module"""

from Web.ApplicationPage import ApplicationPage

from MiscUtils.Funcs import uniqueId
import string, types

import Web.Dialogs
import Web.Ui

class LoginPage(ApplicationPage):
	"""Page providing the real login mechanicsm of the portal.
	
	This page is used by all ApplicationSecurePage derived pages to provide
	login information if the authentication session variables are not set."""
	
	def title(self):
		"""Return page title."""
		return 'Log In'

	def htBodyArgs(self):
		"""Add page body arguments for focusing on the password text box."""
		return ApplicationPage.htBodyArgs(self) + ' onload="document.loginform.password.focus();"' % locals()

	def writeContent(self):
		"""Render page HTML."""
		
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
