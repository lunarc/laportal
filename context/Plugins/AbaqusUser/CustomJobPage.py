#
# LAP Abaqus User subroutine Plugin - Version 0.8
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
import Lap.Utils

import Plugins.AbaqusUser.CustomJob

pluginName = "AbaqusUser"

class CustomJobPage(JobPage):
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["inputFile", "userRoutine"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		adapterName = self.request().adapterName()
		task = Plugins.AbaqusUser.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		return task

	def onCreateEditJobForm(self, task):
		"""Create the form used when editing an existing job definition
		is created."""
	
		form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit Abaqus job", width="26em")
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()
		
		form.beginFieldSet("ABAQUS settings")
		form.addFile("Input file", "inputFile", attribs["inputFile"])
		form.addBreak()
		form.addReadonlyText("Current file", "prevFile", attribs["inputFile"])
		form.addBreak()
		form.addFile("User subroutine", "userRoutine", attribs["userRoutine"])
		form.addBreak()
		form.addReadonlyText("Current file", "prevUserRoutine", attribs["userRoutine"])
		form.addBreak()
		form.addText("License server", "licenseServer", attribs["licenseServer"], fieldType = "hostname")
		form.endFieldSet()
		
		form.beginFieldSet("Job settings")
		form.addText("CPU time (s)", "cpuTime", xrslAttribs["cpuTime"], fieldType = "int")
		form.addBreak()
		form.addText("Job name", "jobName", xrslAttribs["jobName"])
		form.addBreak()
		form.addText("Email notification", "email", xrslAttribs["notify"], fieldType = "email")
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
				
			if fieldValues["licenseServer"] == None:
				errorMessage = "License server required."
									
			return errorMessage
		
		return ""
		
	def onAssignValues(self, task, form):
		
		if form.getName() == "editJobForm":
			
			formFields = form.getFieldValues()
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			attribs["licenseServer"] = formFields["licenseServer"]
			
			xrslAttribs["cpuTime"] = formFields["cpuTime"]
			xrslAttribs["notify"] = formFields["email"]
		
		return ""
	
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""

		if fieldname == "inputFile":
			task.setInputFile(filename)
		
		if fieldname == "userRoutine":
			task.setUserRoutine(filename)

	def onEditAfterCreate(self):
		return True
