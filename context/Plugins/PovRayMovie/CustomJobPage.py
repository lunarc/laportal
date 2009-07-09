#
# LAP PovRay Movie Plugin - Version 0.8
#
# Copyright (C) 2006 Jonas Lindemann
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

from Web.JobPage import JobPage
from time import *
import os
import sys
import pwd
import string
import pickle

import Grid.ARC

import Lap
import Web
import Plugins.PovRayMovie.CustomJob
import Lap.Utils

pluginName = "PovRayMovie"

class CustomJobPage(JobPage):

	def actions(self):
		return JobPage.actions(self)
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["povFilename"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.PovRayMovie.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		return task

	def onCreateEditJobForm(self, task):
	
		form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit PovRay Movie job", width="30em")
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()

		form.beginFieldSet("PovRay settings")
		form.addText("Initial frame ", "startFrame", attribs["startFrame"], fieldType="int")
		form.addBreak()
		form.addText("End frame", "endFrame", attribs["endFrame"], fieldType="int")
		form.addBreak()
		form.addText("Image width", "imageWidth", attribs["imageWidth"], fieldType="int")
		form.addBreak()
		form.addText("Image height", "imageHeight", attribs["imageHeight"], fieldType="int")
		form.endFieldSet()
		
		form.beginFieldSet("PovRay mainfile/archive")
		form.addFile("Povray script", "povFilename", "")
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.endIndent()
		form.addBreak()
		form.addReadonlyText("Current file", "prevFile", attribs["povFilename"])
		form.endFieldSet()				
		
		form.beginFieldSet("Job settings")
		form.addBreak()
		form.addText("CPU time (min)", "cpuTime", xrslAttribs["cpuTime"], fieldType="int")
		form.addBreak()
		form.addText("CPU count", "count", xrslAttribs["count"], fieldType="int")
		form.addBreak()
		form.addText("Job name", "jobName", xrslAttribs["jobName"])
		form.addBreak()
		form.addText("Email notification", "email", xrslAttribs["notify"], fieldType="email")
		form.addHidden("", "oldJobName", xrslAttribs["jobName"])
		form.endFieldSet()
		
		return form
		
	def onValidateValues(self, form):
		
		if form.getName() == "editJobForm":
		
			errorMessage = ""
			
			fieldValues = form.getFieldValues()
			
			if fieldValues["cpuTime"] == 0:
				fieldValues["cpuTime"] == 10
			elif fieldValues["cpuTime"] <1:
				fieldValues["cpuTime"] == 10
													
			return errorMessage
		
		return ""
	
	def onAssignValues(self, task, form):
		
		if form.getName() == "editJobForm":
			
			formFields = form.getFieldValues()
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			for key in formFields.keys():
				print key, " = ", formFields[key]
				attribs[key] = formFields[key]
					
			xrslAttribs["cpuTime"] = formFields["cpuTime"]
			xrslAttribs["notify"] = formFields["email"]
			xrslAttribs["count"] = formFields["count"]
					
		return ""
	
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""

		if fieldname == "povFilename":
			print "-->setPovrayFile()<--"
			task.setPovrayFile(filename)
			
	def onEditAfterCreate(self):
		return True
		

		

