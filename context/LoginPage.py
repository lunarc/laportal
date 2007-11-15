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

from HyperText.HTML import *

import Web.Dialogs
import Web.Ui
import Web.UiExt

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
	
	def onInit(self, adapterName):

		# Create login form
		
		extForm = Web.UiExt.Form(self, "loginform")
		extForm.caption = "Login"
		proxyFile = Web.UiExt.FileField(self, 'proxy', 'Proxy file')
		extForm.add(proxyFile)
		
		self.__loginId = Web.UiExt.Hidden(self, 'loginid')
		self.__loginId.value = 0
		extForm.add(self.__loginId)
		
		buttonSet = Web.UiExt.ButtonSet(self, 'buttonSet')
		loginButton = Web.UiExt.Button(self, 'login', 'Login')
		loginButton.actionEnabled = False
		buttonSet.add(loginButton)

		extForm.add(buttonSet)
		
		self.addExtControl("loginform", extForm)
		
		messageBox = Web.UiExt.MessageBox(self, 'messageBox')
		messageBox.visible = False
		messageBox.URL = self.getPageName()
		
		self.addExtControl("messageBox", messageBox)
		
	def onBeforeRender(self, adapterName):
		
		loginid = uniqueId(self)
		self.session().setValue('loginid', loginid)
		self.__loginId.value = loginid

		extra = self.request().field('extra', None)
		
		if not extra and self.request().isSessionExpired() and not self.request().hasField('logout'):
			extra = 'You have been automatically logged out due to inactivity.'
		
		if extra:
			messageBox = self.getExtControl("messageBox")
			messageBox.visible = True
			messageBox.message = self.htmlEncode(extra)
			messageBox.URL = self.expandPageLoc("LoginPageDummy")
			
			loginForm = self.getExtControl("loginform")
			loginForm.visible = False
			
	def onAfterRender(self, adapterName):

		# Forward any passed in values to the user's intended page after successful login,
		# except for the special values used by the login mechanism itself

		for fieldName, fieldValue in self.request().fields().items():
			if fieldName not in 'login loginid proxy extra logout'.split():
				if isinstance(fieldValue, types.ListType):
					for valueStr in fieldValue:
						self.writeln(INPUT(type="hidden", name=fieldName, value=valueStr))
				else:
						self.writeln(INPUT(type="hidden", name=fieldName, value=fieldValue))
		
		
		

	def writeContent(self):
		"""Render page HTML."""
		
		pass