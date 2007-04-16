#
# ViewOutputPage
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

"""ViewOutputPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes, shutil

from HyperText.HTML import *

import Grid.ARC

import Lap
import Lap.Session
import Lap.Utils

import Web
import Web.Ui
import Web.Dialogs

class ViewOutputPage(ApplicationSecurePage):
	"""Page for displaying text output from grid jobs."""
	
	def title(self):
		"""Return page title"""
		return 'Output view'
			
	def writeHTML(self):
		"""Render HTML for the page.
		
		The page renders the text output from the jobs as text/plain,
		to make sure that is displays correctly and readable."""
			
		jobId = self.getSessionValue("viewOutput_jobId")
		jobName = self.getSessionValue("viewOutput_jobName")
		outputType = self.getSessionValue("viewOutput_type")
		
		response = self.response()
		
		mtype = "text/plain"
		
		response.setHeader('Content-Type',mtype)
		response.flush()

		user = Lap.Session.User(self.session().value('authenticated_user'))
		userDir = user.getDir();
		ui = Grid.ARC.Ui(user)
				
		resultVal = None
		output = None

		if outputType == "stdout":				
			resultVal, output = ui.getStandardOutput(jobId)
		elif outputType == "stderr":
			resultVal, output = ui.getStandardError(jobId)
		elif outputType == "gridlog":
			resultVal, output = ui.getGridLog(jobId)
			
				
		for line in output:
			self.writeln(line.strip())
		
		self.session().setValue("viewfile_filename", "")
						