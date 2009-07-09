#
# LAP PovRay Plugin - Version 0.7
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
import Plugins.PovRay.CustomJob
import Lap.Utils

pluginName = "PovRay"

class CustomJobPage(JobPage):

	def actions(self):
		return JobPage.actions(self)
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["povFile"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.PovRay.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		return task

	def onCreateEditJobForm(self, task):
	
		form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit PovRay job", width="30em")
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()

		form.beginFieldSet("PovRay settings")
		form.addText("Initial frame ", "initialFrame", attribs["initialFrame"], fieldType="int")
		form.addBreak()
		form.addText("End frame", "finalFrame", attribs["finalFrame"], fieldType="int")
		form.addBreak()
		form.addText("Image width", "imageWidth", attribs["imageWidth"], fieldType="int")
		form.addBreak()
		form.addText("Image height", "imageHeight", attribs["imageHeight"], fieldType="int")
		form.addBreak()
		form.addCheck("Antialias", "antialias", attribs["antialias"])
		form.addBreak()
		form.addText("Antialias threshold", "antialiasThreshold", attribs["antialiasThreshold"], fieldType="float")
		form.addBreak()
		form.addText("Antialias depth", "antialiasDepth", attribs["antialiasDepth"], fieldType="float")
		form.endFieldSet()
		
		form.beginFieldSet("PovRay mainfile")
		form.addFile("Povray script", "povFile", "")
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.endIndent()
		form.addBreak()
		form.addReadonlyText("Current file", "prevFile", attribs["povFile"])
		form.endFieldSet()				
		
		form.beginFieldSet("Job settings")
		form.addBreak()
		form.addText("CPU time (min)", "cpuTime", xrslAttribs["cpuTime"], fieldType="int")
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
		
		return ""
	
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""

		if fieldname == "povFile":
			task.setPovrayFile(filename)
			
	def onEditAfterCreate(self):
		return True
		

		

