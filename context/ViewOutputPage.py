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
	
	def title(self):
		return 'Output view'
			
	def writeHTML(self):
			
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
						