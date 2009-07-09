#
# LAP StarSim Plugin - Version 0.8
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
import os, sys, pwd, string, pickle

import Grid.ARC

import Lap
import Web
import Plugins.StarSim.CustomJob
import Lap.Utils

pluginName = "StarSim"

class CustomJobPage(JobPage):
	
	def actions(self):
		return JobPage.actions(self) + ["formNext", "formPrev"]
	
	def getCurrentPage(self):
		if self.session().hasValue("starsim_page"):
			return self.session().value("starsim_page")
		else:
			self.session().setValue("starsim_page", 0)
			return self.session().hasValue("starsim_page")
	
	def formNext(self):
		
		print "formNext"
		currentPage = self.getCurrentPage()
		
		currentPage = currentPage + 1
		
		if currentPage>6:
			currentPage = 6
			
		self.session().setValue("starsim_page", currentPage)
		self.updateForm()
	
	def formPrev(self):

		print "formPrev"
		currentPage = self.getCurrentPage()
		
		if currentPage>0:
			currentPage = currentPage - 1
			
		self.session().setValue("starsim_page", currentPage)
		
		self.updateForm()
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
	
	def onGetFileTransferFields(self):
		return ["psf", "object_coordfile", "back_coordfile"]

	def onCreateNewTask(self):
		"""Create the derived task class and return it to the parent class."""
	
		task = Plugins.StarSim.CustomJob.CustomTask()
		task.setTaskEditPage("/Plugins/%s/CustomJobPage" % pluginName)
		self.session().setValue("starsim_page", 0)
		return task
	
	def createControls(self, paramValues, paramOrder, attribs, form):
		for paramName in paramOrder:
			param = paramValues[paramName]
			form.setUnit(param[2])
			if param[3] == "file":
				form.addFile(param[1], paramName, "")
				form.addBreak()
				if paramName == "psf" and attribs[paramName]=="":
					form.addReadonlyText("Default file", paramName+"Hidden", attribs["psf_default"])
				elif paramName == "object_coordfile" and attribs[paramName]=="":
					form.addReadonlyText("Default file", paramName+"Hidden", attribs["object_coordfile_default"])				
				elif paramName == "back_coordfile" and attribs[paramName]=="":
					form.addReadonlyText("Default file", paramName+"Hidden", attribs["back_coordfile_default"])				
				else:
					form.addReadonlyText("Current file", paramName+"Hidden", attribs[paramName])
				form.addBreak()
			elif param[3] == "choice":
				choices = param[4]
				form.beginSelect(param[1], paramName)
				for choice in choices:
					if attribs["psfflag"] == choice:
						form.addOption(choice, selected=True)
					else:
						form.addOption(choice, selected=False)
				form.endSelect()
			else:
				form.addText(param[1], paramName, str(attribs[paramName]), fieldType = param[3])
			form.addBreak()
		

	def onCreateEditJobForm(self, task):
		"""Create the form used when editing an existing job definition
		is created."""
		
		if not self.session().hasValue("starsim_page"):
			self.session().setValue("starsim_page", 0)
			
		currentPage = self.session().value("starsim_page")
		
		print "currentPage =", currentPage
		
		form = None
		
		if currentPage == 0:
	
			form = Web.Ui.Form("editJobAstrophysics", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="32em")
			form.setHaveGuideButtons(False, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("15em")
			
			paramOrder = Plugins.StarSim.CustomJob.astrophysicsParamOrder
			paramValues = Plugins.StarSim.CustomJob.astrophysicsParams
			
			form.beginFieldSet("Astrophysics")
			self.createControls(paramValues, paramOrder, attribs, form)
			form.endFieldSet()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])
											
		
		if currentPage == 1:
	
			form = Web.Ui.Form("editJobTelescope", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="32em")
			form.setHaveGuideButtons(True, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("17em")
			
			paramOrder = Plugins.StarSim.CustomJob.telescopeParamOrder
			paramValues = Plugins.StarSim.CustomJob.telescopeParams
			
			form.beginFieldSet("Telescope")
			self.createControls(paramValues, paramOrder, attribs, form)
			form.endFieldSet()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])

		if currentPage == 2:
	
			form = Web.Ui.Form("editJobFormInstrument", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="35em")
			form.setHaveGuideButtons(True, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("17em")
			form.setDefaultUnitWidth("10em")
			
			paramOrder = Plugins.StarSim.CustomJob.instrumentalParamOrder
			paramValues = Plugins.StarSim.CustomJob.instrumentalParams
			
			form.beginFieldSet("Instrument")
			self.createControls(paramValues, paramOrder, attribs, form)
			form.endFieldSet()
			
			form.resetDefaultUnitWidth()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])
			
		if currentPage == 3:
			
			form = Web.Ui.Form("editJobFormPsfType", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="32em")
			form.setHaveGuideButtons(True, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("15em")
			
			paramOrder = Plugins.StarSim.CustomJob.psfTypeOrder
			paramValues = Plugins.StarSim.CustomJob.psfTypeParams
			
			form.beginFieldSet("PSF Type")
			self.createControls(paramValues, paramOrder, attribs, form)
			form.endFieldSet()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])			

		if currentPage == 4:
	
			form = Web.Ui.Form("editJobFormPSF", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="32em")
			form.setHaveGuideButtons(True, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			if attribs["psfflag"] == "analytical":
			
				form.setDefaultLabelWidth("15em")
				
				paramOrder = Plugins.StarSim.CustomJob.psfAnalyticalOrder
				paramValues = Plugins.StarSim.CustomJob.psfAnalyticalParams
				
				form.beginFieldSet("Analytical")
				self.createControls(paramValues, paramOrder, attribs, form)
				form.endFieldSet()
				
			else:
				
				form.setDefaultLabelWidth("15em")
				
				paramOrder = Plugins.StarSim.CustomJob.psfOpdParamOrder
				paramValues = Plugins.StarSim.CustomJob.psfOpdParams
				
				form.beginFieldSet("Opd Params")
				self.createControls(paramValues, paramOrder, attribs, form)
				form.endFieldSet()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])

		if currentPage == 5:
	
			form = Web.Ui.Form("editJobDataHandling", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="40em")
			form.setHaveGuideButtons(True, True)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("22em")
			
			paramOrder = Plugins.StarSim.CustomJob.dataHandlingParamOrder
			paramValues = Plugins.StarSim.CustomJob.dataHandlingParams
			
			form.beginFieldSet("Data handling")
			self.createControls(paramValues, paramOrder, attribs, form)
			form.endFieldSet()
			
			form.addHidden("", "jobName", xrslAttribs["jobName"])
			form.addHidden("", "oldJobName", xrslAttribs["jobName"])

		elif currentPage == 6:
			
			form = Web.Ui.Form("editJobFormSettings", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit StarSim job", width="30em")
			form.setHaveGuideButtons(True, False)
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			form.setDefaultLabelWidth("10em")
													
			form.beginFieldSet("Job settings")
			form.addText("Number of CPU:s", "cpuCount", xrslAttribs["count"])
			form.addBreak()
			form.addText("CPU time (min)", "cpuTime", xrslAttribs["cpuTime"], fieldType = "int")
			form.addBreak()
			form.addText("Job name (prefix)", "jobName", self.getJobName())
			form.addBreak()
			form.addText("Email notification", "email", xrslAttribs["notify"], fieldType = "email")
			form.addHidden("", "oldJobName", self.getJobName())
			form.endFieldSet()
					
			form.setControlHelp("cpuTime", "Expected CPU time needed for the job to complete.")
			form.setControlHelp("jobName", "A descriptive name used to identify the job on the Grid.")
			form.setControlHelp("email", "The job can send status notifications to the given email address.")
		
		return form
		
	def onValidateValues(self, form):
		
		if form.getName() == "editJobFormSettings":
		
			errorMessage = ""
			
			fieldValues = form.getFieldValues()
			
			if fieldValues["cpuTime"] == 0:
				fieldValues["cpuTime"] == 10
			elif fieldValues["cpuTime"] <1:
				fieldValues["cpuTime"] == 10
													
			return errorMessage
		
		return ""
	
	def onAssignValues(self, task, form):
		
		formFields = form.getFieldValues()
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()

		if form.getName() == "editJobFormSettings":
			
			xrslAttribs["jobName"] = formFields["jobName"]	
			xrslAttribs["cpuTime"] = formFields["cpuTime"]
			xrslAttribs["notify"] = formFields["email"]
			xrslAttribs["count"] = formFields["cpuCount"]
			
		elif form.getName() == "edtJobPsfType":

			for key in formFields.keys():
				print key, " = ", formFields[key]
				attribs[key] = formFields[key]
				

			xrslAttribs["jobName"] = formFields["jobName"]					
			
		else:
			for key in formFields.keys():
				print key, " = ", formFields[key]
				attribs[key] = formFields[key]

			xrslAttribs["jobName"] = formFields["jobName"]					
		
		return ""
	
	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files."""

		if fieldname == "psf":
			task.setPSFFilename(filename)
			
		if fieldname == "object_coordfile":
			task.setObjectCoordFilename(filename)
			
		if fieldname == "back_coordfile":
			task.setBackCoordFilename(filename)
			
	def onEditAfterCreate(self):
		return True
	
	def onLeaveForm(self):
		if self.session().hasValue("starsim_page"):
			self.session().delValue("starsim_page")
	
