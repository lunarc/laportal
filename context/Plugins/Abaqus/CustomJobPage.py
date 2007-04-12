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
import Plugins.Abaqus.CustomJob
import Lap.Utils

import Plugins.AbaqusUser.CustomJob

pluginName = "Abaqus"

class CustomJobPage(JobPage):
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["inputFile", "userRoutine"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.Abaqus.CustomJob.CustomTask()
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
		form.addText("License server", "licenseServer", attribs["licenseServer"], fieldType="hostname")
		form.endFieldSet()
		
		form.beginFieldSet("Job settings")
		form.addText("CPU time (s)", "cpuTime", xrslAttribs["cpuTime"], fieldType="int")
		form.addBreak()
		form.addText("Job name", "jobName", xrslAttribs["jobName"])
		form.addBreak()
		form.addText("Email notification", "email", xrslAttribs["notify"], fieldType="email")
		form.addHidden("", "oldJobName", xrslAttribs["jobName"])
		form.endFieldSet()
		
		form.setControlHelp("inputFile", "Select the ABAQUS input file to be used using the Browse button.")
		form.setControlHelp("licenseServer", "Specifiy the hostname of the ABAQUS license server to be used.")
		form.setControlHelp("cpuTime", "Expected CPU time needed for the job to complete.")
		form.setControlHelp("jobName", "A descriptive name used to identify the job on the Grid.")
		form.setControlHelp("email", "The job can send status notifications to the given email address.")	
		
		return form
	
	def onValidateValues(self, form):

		if form.getName() == "editJobForm":
		
			errorMessage = ""
			
			fieldValues = form.getFieldValues()
			
			if fieldValues["cpuTime"] == 0:
				fieldValues["cpuTime"] == 10
			elif fieldValues["cpuTime"] <1:
				fieldValues["cpuTime"] == 10
				
			print "licenseServer = ", fieldValues["licenseServer"]
				
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

	def onEditAfterCreate(self):
		return True
	
	def onReturnPageName(self):
		return "Plugins/%s/CustomJobPage" % (pluginName)
