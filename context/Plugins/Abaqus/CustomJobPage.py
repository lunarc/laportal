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
	
	def onAssignFormValues(self, task, form):
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()
		
		print form.controlDict
		print attribs
		
		form.controlDict["inputFile"].value = attribs["inputFile"]
		form.controlDict["licenseServer"].value = attribs["licenseServer"]
		form.controlDict["cpuTime"].value = xrslAttribs["cpuTime"]
		form.controlDict["jobName"].value = xrslAttribs["jobName"]
		form.controlDict["email"].value = xrslAttribs["notify"]
		form.controlDict["oldJobName"].value = xrslAttribs["jobName"]

	def onCreateEditJobForm(self, task=None):
		"""Create the form used when editing an existing job definition
		is created."""

		form = Web.UiExt.Form(self, "editJobForm")
		form.caption = "Edit ABAQUS job"
		
		settingsFieldSet = Web.UiExt.FieldSet(self)
		settingsFieldSet.legend = "ABAQUS settings"
		
		inputFile = Web.UiExt.FileField(self, "inputFile", "Input file")
		prevFile = Web.UiExt.TextField(self, "prevFile", "Current file")
		
		settingsFieldSet.add(inputFile)
		settingsFieldSet.add(prevFile)
		
		licenseServer = Web.UiExt.TextField(self, "licenseServer", "License server")
		
		settingsFieldSet.add(licenseServer)
		
		form.add(settingsFieldSet)
		
		jobSettingsFieldSet = Web.UiExt.FieldSet(self)
		jobSettingsFieldSet.legend = "Job settings"
		
		cpuTime = Web.UiExt.TextField(self, "cpuTime", "CPU time (minutes)")

		jobName = Web.UiExt.TextField(self, "jobName", "Job name")
		oldJobName = Web.UiExt.Hidden(self, "oldJobName")
		
		email = Web.UiExt.TextField(self, "email", "Email address")
		
		jobSettingsFieldSet.add(cpuTime)
		jobSettingsFieldSet.add(jobName)
		jobSettingsFieldSet.add(oldJobName)
		jobSettingsFieldSet.add(email)
		
		form.add(jobSettingsFieldSet)
	
		#form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit Abaqus job", width="26em")
		#
		#
		#form.beginFieldSet("ABAQUS settings")
		#form.addFile("Input file", "inputFile", attribs["inputFile"])
		#form.addBreak()
		#form.addReadonlyText("Current file", "prevFile", attribs["inputFile"])
		#form.addBreak()
		#form.addText("License server", "licenseServer", attribs["licenseServer"], fieldType="hostname")
		#form.endFieldSet()
		#
		#form.beginFieldSet("Job settings")
		#form.addText("CPU time (s)", "cpuTime", xrslAttribs["cpuTime"], fieldType="int")
		#form.addBreak()
		#form.addText("Job name", "jobName", xrslAttribs["jobName"])
		#form.addBreak()
		#form.addText("Email notification", "email", xrslAttribs["notify"], fieldType="email")
		#form.addHidden("", "oldJobName", xrslAttribs["jobName"])
		#form.endFieldSet()
		#		
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
