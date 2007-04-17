#
# SyncJobsPage
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

"""SyncJobsPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId
import string, types

import Grid.ARC
import Lap.Session

class SyncJobsPage(ApplicationSecurePage):
	"""Placeholder page for synchronizing the job list.
	
	When job synchronization has been completed the page redirects
	to the ManageJobPage page."""
	
	def title(self):
		"""Return page title."""
		return 'Syncronising jobs'

	def writeContent(self):
		"""Render page HTML"""
		user = Lap.Session.User(self.session().value('authenticated_user'))
		ui = Grid.ARC.Ui(user)
		
		ui.sync()
		
		self.sendRedirectAndEnd("ManageGridJobPage")

