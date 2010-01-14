#
# LoginPageDummy
#
# Copyright (C) 2006-2008 Jonas Lindemann
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

"""LogoutPageDummy module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs

class LoginPageDummy(ApplicationSecurePage):
	"""Page that is used to initiate a login.
	
	Handles the case when the users selects login in the menu. All pages
	derived from ApplicationSecurePage provide a login facility automatically,
	so this page is a "Dummy". Succesful login redirects to SecureWelcomePage."""
	
	def title(self):
		"""Return page title."""
		return 'Logged in'

	def writeContent(self):
		"""Render page HTML."""
		
		adapterName = self.request().adapterName()
		
		if self.loggedInUserDN()!=None:
			DN = self.loggedInUserDN()
			Web.Dialogs.messageBox(self, "%s logged in." % DN, "Information", "%s/context/SecureWelcomePage" % adapterName)
		elif self.loggedInUser()!=None:
			user = self.loggedInUser()
			Web.Dialogs.messageBox(self, "% logged in." % user, "Information", "%s/context/SecureWelcomePage" % adapterName)

