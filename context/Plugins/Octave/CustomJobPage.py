#
# LAP Octave Single Plugin - Version 0.8
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

import Plugins.Octave.CustomJob

pluginName = "Octave"

class CustomJobPage(JobPage):
	
	def actions(self):
		return JobPage.actions(self) + ["clearPackageFiles", "clearExtraFiles",
										"removePackageFiles", "removeExtraFiles" ]	
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["mainFile", "packageFile"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.Octave.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		return task

	def onCreateEditJobForm(self, task):
		"""Create the form used when editing an existing job definition
		is created."""
	
		form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit OCTAVE job", width="30em")
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()
		
		form.beginFieldSet("OCTAVE toolkit packages")
		form.beginSelect("Package files", "packageFiles", size=4, width="20em")
		for package in attribs["packages"]:
			print "Adding package."
			form.addOption(package)
		form.endSelect()
		form.addBreak()
		form.addFile("Add package file(s) (*.zip)", "packageFile", "")
		form.addBreak()
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.addSubmitButton("Clear", "_action_clearPackageFiles")
		form.addSubmitButton("Remove", "_action_removePackageFiles")
		form.endIndent()
		form.endFieldSet()
		
		form.beginFieldSet("Additional files")
		form.beginSelect("Additional files", "extraFiles", size=4, width="20em")
		for extraFile in attribs["extra"]:
			form.addOption(extraFile)
		form.endSelect()
		form.addBreak()
		form.addFile("Add additional file(s)", "extraFile", "")
		form.addBreak()
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.addSubmitButton("Clear", "_action_clearExtraFiles")
		form.addSubmitButton("Remove", "_action_removeExtraFiles")
		form.endIndent()
		form.endFieldSet()
		
		form.beginFieldSet("MATLAB main file")
		form.addFile("Main file", "mainFile", "")
		form.addBreak()
		form.beginIndent("9.0em")
		form.addSubmitButton("Upload", "_action_uploadFile")
		form.endIndent()
		form.addBreak()
		form.addReadonlyText("Current file", "prevFile", attribs["mainFile"])
		form.endFieldSet()		
		
		form.beginFieldSet("Job settings")
		form.addBreak()
		form.addText("CPU time (min)", "cpuTime", xrslAttribs["cpuTime"], fieldType = "int")
		form.addBreak()
		form.addText("Job name", "jobName", xrslAttribs["jobName"])
		form.addBreak()
		form.addText("Email notification", "email", xrslAttribs["notify"], fieldType = "email")
		form.addHidden("", "oldJobName", xrslAttribs["jobName"])
		form.endFieldSet()
				
		form.setControlHelp("mainFile", "Select the Octave main file to be used using the Browse button.")
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
													
			return errorMessage
		
		return ""
		
	def onAssignValues(self, task, form):
		
		if form.getName() == "editJobForm":
			
			formFields = form.getFieldValues()
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			xrslAttribs["cpuTime"] = formFields["cpuTime"]
			xrslAttribs["notify"] = formFields["email"]
		
		return ""
	
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""

		if fieldname == "mainFile":
			task.setMainFile(filename)
			
		if fieldname == "packageFile":
			task.addPackage(filename)
			
		if fieldname == "extraFile":
			task.addExtraFile(filename)
			
	def onEditAfterCreate(self):
		return True

	def clearPackageFiles(self):
		task = self.getTask()
		task.clearPackages()
		self.redrawForm()
	
	def removePackageFiles(self):
		task = self.getTask()
		
		removeFilename = self.getString(self.request(), "packageFiles")
		
		if removeFilename!="":
			task.removePackage(removeFilename)
			
		self.redrawForm()
			
	def clearExtraFiles(self):
		task = self.getTask()
		task.clearExtraFiles()
		self.redrawForm()
	
	def removeExtraFiles(self):
		task = self.getTask()
		
		print self.request().fields()
		
		removeFilename = self.getString(self.request(), "extraFiles")
		
		if removeFilename!="":
			task.removeExtraFile(removeFilename)
			
		self.redrawForm()			
