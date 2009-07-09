#
# SecureWelcomePage
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

"""SecureWelcomePage module"""

from Web.UserSecurePage import UserSecurePage

class UserSecureWelcomePage(UserSecurePage):
	"""Secure version of the welcome page
	
	This page is used as welcome page when the user is logged in to the
	portal, displaying the complete menubar."""

	def title(self):
		return 'Welcome!'
	

