#
# UserAdminPage
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

"""UserAdminPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

import LapSite

import os, re

class UserAdminPage(ApplicationSecurePage):
	"""Maintains a list of DN and username mappings.
	
	The list of authorised users is listed in the 
	file, userlist.txt, and is located in LapSite.Dirs["SessionDir"]
	
	Only the portal admin user can use this page."""
	
	def actions(self):
		"""Return implemented actions."""
		return ApplicationSecurePage.actions(self) + ["add", "remove"]	
	
	def title(self):
		"""Return page title"""
		return 'User Administration Page'
	
	def writeContent(self):
		"""Render the text HTML"""
		
		# Retrieve user settings
		
		sessionDir = LapSite.Dirs["SessionDir"]
		userListFilename = os.path.join(sessionDir, "userlist.txt")
		
		userList = []
		userDict = {}

		if self.isUserAdminUser():
			
			if os.path.exists(userListFilename):
				userListFile = file(userListFilename)
				lines = userListFile.readlines()
				userListFile.close()
				
				for line in lines:
					userDN = line.strip()
					if not userDict.has_key(userDN):
						userList.append(line.strip())
						userDict[userDN] = userDN

			self.session().setValue("useradmin_userList", userList)
			self.session().setValue("useradmin_userDict", userDict)
					
			form = Web.Ui.Form("UserAdminPage", "%s/UserAdminPage" % self.pageLoc(), "User Administration", "40em")
			
			form.beginSelect("Allowed users", "userList", size=10, width = "35em")
			for userDN in userList:
				form.addOption(userDN)
			form.endSelect()
			
			form.addText("User DN", "userDN", value = "", width="20em", labelWidth="", fieldType="string")
			form.addBreak()

			form.addFormButton("Add", "_action_add")
			form.addFormButton("Remove", "_action_remove")
			
			form.setHaveSubmit(False)
			
			form.render(self)

		else:
			Web.Dialogs.messageBox(self, "You are not site administrator", title="Message")
			
	def add(self):
		"""Add DN/username mapping the the VO list file."""
		
		# Get the session directory
		
		sessionDir = LapSite.Dirs["SessionDir"]
		userListFilename = os.path.join(sessionDir, "userlist.txt")
		
		# Retrieve userDN and local account from the request

		userDN = self.getURLString(self.request(), "userDN")

		# Append the DN to the voList
		
		userList = self.session().value("useradmin_userList")
		userDict = self.session().value("useradmin_userDict")
		
		if not userDict.has_key(userDN):
			userList.append(userDN)
			userDict[userDN] = userDN
		
		# Write user list to file
		
		userListFile = file(userListFilename, "w")
		
		for userDN in userList:
			userListFile.write(userDN+"\n")
			
		userListFile.close()
		
		self.writeBody()
	
	def remove(self):
		"""Remove DN/username mapping from VO list file."""
		
		# Get the session directory
		
		sessionDir = LapSite.Dirs["SessionDir"]
		userListFilename = os.path.join(sessionDir, "userlist.txt")
		
		# Retrieve userDN and local account from the request
		
		selectedItem = self.getURLString(self.request(), "userList")

		if selectedItem=="":
			return
		
		userDN = selectedItem
				
		# Remove DN from Vo list
		
		userList = self.session().value("useradmin_userList")
		
		i = 0
		
		for i in range(len(userList)):
			if userList[i] == userDN:
				del userList[i]
				break
			
		# Write user list to file
		
		userListFile = file(userListFilename, "w")
		
		for userDN in userList:
			userListFile.write(userDN)
			
		userListFile.close()
					
		self.writeBody()
