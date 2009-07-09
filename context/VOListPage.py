#
# VOListPage
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

"""VOListPage module"""

from WebKit.Page import Page

import Web.Dialogs
import Web.Ui
import Lap.Session

import LapSite

import os, re

class VOListPage(Page):
	"""Displays a text list of users in the portal VO.
	
	This list can be directly used by middlewares such as ARC to authorise
	users on comptuer resources."""
	
	def writeHTML(self):
		"""Write a text/plain page width the list of DN and username mappings.
		
		The format is:
		
		"{DN1}" {unix username}
		...
		"{DNn}" {unxi username}
		"""

		# Retrieve user settings

		self.response().setHeader('Content-Type', 'text/plain')
		self.response().setHeader('Content-Disposition', 'inline')
		
		# Check if remote address is allowed to receive VO-list
		
		remoteAddress = self.request().environ()["REMOTE_ADDR"]
		sessionDir = LapSite.Dirs["SessionDir"]
		voSites = LapSite.Admin["VOSites"]
		
		authorisedSite = False
		
		for site in voSites:
			if remoteAddress.strip() == site.strip():
				authorisedSite = True
				
		if authorisedSite:
			
			# Write out authorised VO-list
		
			voListFilename = os.path.join(sessionDir, "volist.txt")
			
			voList = []
	
			if os.path.exists(voListFilename):
				voListFile = file(voListFilename)
				lines = voListFile.readlines()
				voListFile.close()
				
				for line in lines:
					mapping = re.match('"(.*)"\s*(.*)', line).groups()
					if len(mapping) == 2:
						self.writeln('"'+mapping[0]+'" '+mapping[1])			
