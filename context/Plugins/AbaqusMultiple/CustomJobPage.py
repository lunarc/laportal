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

import Plugins.AbaqusMultiple.CustomJob

pluginName = "AbaqusMultiple"

class CustomJobPage(JobPage):
	
	def actions(self):
		return JobPage.actions(self) + ["clearInputFiles", "removeInputFiles"]	
		
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		"""Return file transfer form controls"""
		return ["addInputFile"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.AbaqusMultiple.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		return task
	
	def onCreateEditJobForm(self, task):
		"""Create a form used to edit an existing job definition. The method
		should return a form instance."""
	
		form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit Abaqus job", width="30em")
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()
		
		form.beginFieldSet("ABAQUS input files")
		form.beginSelect("Input files", "inputFiles", size=8, width="20em")
		for inputFile in attribs["inputFiles"]:
				form.addOption(inputFile)
		form.endSelect()
		form.addBreak()
		form.addFile("Add input file(s)", "addInputFile", "inputFile")
		form.addBreak()
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.addSubmitButton("Clear", "_action_clearInputFiles")
		form.addSubmitButton("Remove", "_action_removeInputFiles")
		form.endIndent()
		form.endFieldSet()
		
		form.beginFieldSet("ABAQUS settings")
		form.addText("License server", "licenseServer", attribs["licenseServer"], fieldType="hostname")
		form.endFieldSet()

		
		form.beginFieldSet("Job settings")
		if attribs.has_key("multipleJobs"):
			if attribs["multipleJobs"]:
				form.addCheck("Multiple jobs", "multipleJobs", True)
			else:
				form.addCheck("Multiple jobs", "multipleJobs", False)
		else:
			form.addCheck("Multiple jobs", "multipleJobs", False)
			
		form.addBreak()
		form.addText("CPU time (min.)", "cpuTime", xrslAttribs["cpuTime"], fieldType="int")
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
			attribs["multipleJobs"] = formFields["multipleJobs"]
			
			xrslAttribs["cpuTime"] = formFields["cpuTime"]
			xrslAttribs["notify"] = formFields["email"]
		
		return ""
		
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""
		
		if fieldname == "addInputFile":
			task.addInputFile(filename)
				
	def onEditAfterCreate(self):
		"""Return True to display the edit form when the create form has
		been completed."""
		return True
	
	def clearInputFiles(self):
		task = self.getTask()
		task.clearInputFiles()
		self.redrawForm()
	
	def removeInputFiles(self):
		
		form = self.getForm()
		form.retrieveFieldValues(self.request())
		fieldValues = form.getFieldValues()
		
		removeFilename = fieldValues["inputFiles"]
		
		task = self.getTask()
		
		if removeFilename!=None:
			task.removeInputFile(removeFilename)
			
		self.redrawForm()

	
