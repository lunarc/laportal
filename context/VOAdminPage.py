#
# VOAdminPage
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

"""VOAdminPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

import Web.Dialogs
import Web.Ui
import Lap.Session

import LapSite

import os, re

class VOAdminPage(ApplicationSecurePage):
	"""Maintains a list of DN and username mappings.
	
	The list of DN/username mappings are stored in a normal text
	file, volist.txt, and is located in LapSite.Dirs["SessionDir"]
	
	Only the portal admin user can use this page."""
	
	def actions(self):
		"""Return implemented actions."""
		return ApplicationSecurePage.actions(self) + ["add", "remove"]	
	
	def title(self):
		"""Return page title"""
		return 'VO Administration Page'
	
	def writeContent(self):
		"""Render the text HTML"""
		
		# Retrieve user settings
		
		sessionDir = LapSite.Dirs["SessionDir"]
		voListFilename = os.path.join(sessionDir, "volist.txt")
		
		voList = []

		if self.isVOAdminUser():
			
			if os.path.exists(voListFilename):
				voListFile = file(voListFilename)
				lines = voListFile.readlines()
				voListFile.close()
				
				for line in lines:
					mapping = re.match('"(.*)"\s*(.*)', line).groups()
					print "line =", line
					print "mapping =", mapping
					if len(mapping)==2:
						voList.append([mapping[0], mapping[1]])
						
			self.session().setValue("voadmin_voList", voList)
					
			form = Web.Ui.Form("VOAdminPAge", "%s/VOAdminPage" % self.pageLoc(), "Portal VO Administration", "40em")
			
			form.beginSelect("VO Users", "voList", size=10, width = "35em")
			for mapping in voList:
				form.addOption(mapping[0] + " - " + mapping[1])
			form.endSelect()
			
			form.addText("User DN", "userDN", value = "", width="20em", labelWidth="", fieldType="string")
			form.addBreak()
			form.addText("Local unix account", "localAccount", value = "", width="10em", labelWidth="", fieldType="string")
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
		voListFilename = os.path.join(sessionDir, "volist.txt")
		
		# Retrieve userDN and local account from the request

		userDN = self.getURLString(self.request(), "userDN")
		localAccount = self.getString(self.request(), "localAccount")
		
		# Append the DN to the voList
		
		voList = self.session().value("voadmin_voList")
		voList.append([userDN, localAccount])
		
		# Write VO list to file
		
		voListFile = file(voListFilename, "w")
		
		for mapping in voList:
			voListFile.write('"%s" %s\n' % (mapping[0], mapping[1]))
			
		voListFile.close()
		
		self.writeBody()
	
	def remove(self):
		"""Remove DN/username mapping from VO list file."""
		
		# Get the session directory
		
		sessionDir = LapSite.Dirs["SessionDir"]
		voListFilename = os.path.join(sessionDir, "volist.txt")
		
		# Retrieve userDN and local account from the request
		
		selectedItem = self.getURLString(self.request(), "voList")

		if selectedItem=="":
			return
		
		userDN = selectedItem.split("-")[0].strip()
		localAccount = selectedItem.split("-")[1].strip()
				
		# Remove DN from Vo list
		
		voList = self.session().value("voadmin_voList")
		
		i = 0
		
		for i in range(len(voList)):
			if voList[i][0] == userDN:
				del voList[i]
				break
			
		# Write VO list to file
		
		voListFile = file(voListFilename, "w")
		
		for mapping in voList:
			voListFile.write('"%s" %s\n' % (mapping[0], mapping[1]))
			
		voListFile.close()
					
		self.writeBody()
