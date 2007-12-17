#
# LogoutPage
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

import Web.UiExt

class LogoutPage(ApplicationPage):
	"""Page for displaying a logout confirmation. Clicking OK returns to the
	WelcomePage."""
	
	def title(self):
		"""Return page title."""
		return 'Log Out'
	
	def onInit(self, adapterName):
		messageBox = Web.UiExt.MessageBox(self, 'messageBox')
		messageBox.message = "You have been logged out."
		messageBox.URL = self.expandPageLoc("WelcomePage")
		self.addExtControl("messageBox", messageBox)
		
	def onAfterRender(self, adapterName):
		self.session().invalidate()
