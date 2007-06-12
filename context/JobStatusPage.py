#
# JobStatusPage
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

"""JobStatusPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId
import string, types, time, os

from HyperText.HTML import *

import Web.Dialogs
import Web.Ui
import Lap.Session
import Grid.ARC

class JobStatusPage(ApplicationSecurePage):
	"""OBSOLETE, do not use."""
	def title(self):
		return 'Job status'

	def onInit(self, adapterName):
		"""Initialise page."""
		self._dialog = Web.Ui.ExtBasicDialog(self, "extdialog", width=800, height=400)
		self.addExtControl(self._dialog)
		self._grid = Web.Ui.ExtGrid(self, "extgrid", 6, 6)
		self.addExtControl(self._grid)
	
	def onUseTooltips(self):
		return False
	
	def onUseExtJS(self):
		return True
	
	def writeContent(self):
		
		# Get user information
		
		user = Lap.Session.User(self.session().value('authenticated_user'))
		ui = Grid.ARC.Ui(user)
		
		# Get user job list database
		
		jobListFilename = os.path.join(user.getDir(),"jobList.db")
		jobList = Grid.ARC.JobList(jobListFilename)
		jobDict = jobList.get()
		
		# Create a grid representing the job list database
		
		self._grid.setSize(len(jobDict.keys()), 5)
		self._grid.setHeaders(["Status", "Job id", "Exit code", "Job name", "Information"])
		
		row = 0
		
		for key in jobDict.keys():
			self._grid.setItems(row, [jobDict[key][0], jobDict[key][1], jobDict[key][2], jobDict[key][3]])
			content = ""
			if len(jobDict[key][4])>0:
				for line in jobDict[key][4]:
					content = content + line + "<br>"
					
				print content
				self._grid.setItem(row, 4, content)
				
			row += 1
			
		# Render grid
		
		grid = self._grid.renderToTag()
		self._dialog.setContent(grid)
		dialog = self._dialog.renderToTag()
			
		self.writeln(dialog)
				