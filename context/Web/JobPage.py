#
# JobPage base class module
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

"""JobPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from time import *

import os
import sys
import pwd
import string
import pickle

import Grid.ARC

import Lap
import Lap.Session
from Lap.Log import *

import Web
import Web.Ui
import Web.Dialogs

# Explorer file upload example:
# C:\Documents and Settings\Göran\Skrivbord\portal\abaqus\t1-std.inp

class JobPage(ApplicationSecurePage):
	"""Base class for job plugins
	
	This class provides all the neccesary functions for editing
	job definitions."""
	
	# ----------------------------------------------------------------------
	# Private methods
	# ----------------------------------------------------------------------	

	def _uploadFile(self, fieldName, destDir):
		"""Handles a HTTP file upload request from the
		request file, fieldName, and copies it to the directory
		specified by destDir."""
		if self.request().hasField(fieldName):

			filename = ""

			ok = True
			try:
				f = self.request().field(fieldName)
				fileContent = f.file.read()
				
				
				if f.filename.find("\\")!=-1:
					lapDebug("Explorer upload...")
					
					lastBackslash = f.filename.rfind("\\")
					filename = f.filename[lastBackslash+1:]
					lapDebug("modified filename = " + filename)
				else:
					filename = f.filename
					
				lapDebug("Upload filename = " + filename)
				inputFile = file(os.path.join(destDir, filename), "w")
				inputFile.write(fileContent)
				inputFile.close()
			except:
				ok = False
				pass
			
			if ok:
				lapInfo("File, %s, uploaded to %s." % (filename, destDir))
				return ok, filename
			else:
				return ok, ""
			
		else:
			return False, ""
		
	def _getSessionValue(self, keyName):
		"""Returns a session value if exists, otherwise it returns
		None."""
		if self.session().hasValue(keyName):
			return self.session().value(keyName)
		else:
			return None
		
	# ----------------------------------------------------------------------
	# Get/set methods
	# ----------------------------------------------------------------------	
		
	def getTask(self):
		"""Convenience function for retrieving the current session task."""
		return self._getSessionValue("jobpage_task")
	
	def getForm(self):
		"""Convenience function for retrieving the current session task."""
		return self.__form
		#return self._getSessionValue("jobpage_form")
	
	def getJobName(self):
		"""Convenience function for retrieveing the current job name."""
		return self._getSessionValue("jobpage_jobname")
	
	def getJobDir(self):
		"""Convenience function for retrieveing the current job dir"""
		return self._getSessionValue("jobpage_jobdir")
			
	def setFormInfo(self, status):
		"""Set text to display as an information window when the page is redrawn."""
		self.session().setValue("jobpage_info", status)		

	def setFormStatus(self, status, returnPage = ""):
		"""Set text for a status message.
		
		The returnPage parameter can be used to set a different return page
		for the button in the status window."""
		
		if returnPage=="":
			returnPageName = self.onReturnPageName()
			returnPage = self.pageLoc()+"/%s" % (returnPageName)
		
		self.session().setValue("jobpage_status", status)
		self.session().setValue("jobpage_return_page", returnPage)
		
	def setFormMessage(self, message):
		"""Set text to display as a message when the page is redrawn."""
		self.session().setValue("jobpage_message", message)
		
	# ----------------------------------------------------------------------
	# Methods
	# ----------------------------------------------------------------------	
		
	def cleanSession(self):
		"""Clean the current session information used by the JobPage class."""
		if self.session().hasValue("jobpage_editing"):
			self.session().delValue("jobpage_editing")
		if self.session().hasValue("jobpage_task"):
			self.session().delValue("jobpage_task")
		if self.session().hasValue("jobpage_jobdir"):
			self.session().delValue("jobpage_jobdir")
		#if self.session().hasValue("jobpage_form"):
		#	self.session().delValue("jobpage_form")

	def cleanup(self):
		"""Handle cleanup action."""
		try:
			for filename in os.listdir(self.jobDir):
				os.remove(os.path.join(self.jobDir, filename))
			os.rmdir(self.jobDir)
		except:
			pass
		
	def redrawForm(self):
		"""Convenience function for redrawing form."""
		jobName = self.getString(self.request(), "jobName")
		if jobName != "":
			self.session().setValue("jobpage_editing", jobName)
			self.session().setValue("jobpage_keep_edit", "")
		self.writeBody()
		
	def updateForm(self):
		"""Redraw form."""
		self.modify(confirmation = False)
		self.session().setValue("jobpage_editing", "")
		self.writeBody()
		
	def isEditing(self):
		"""Return true if session is editing."""
		return self.session().hasValue("editjob")		
		
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------
	
	def onInit(self, adapterName):
		form = self.onCreateEditJobForm()
		form.visible = False
		self.addControl("mainForm", form)
		
	def onBeforeRender(self, adapterName):
		
		if self.request().hasField("editjob"):
			
			# Get neccessary info
			
			mainForm = self.getControl("mainForm")
			mainForm.visible = True
			
			self.cleanSession()
			
			jobName = ""
			jobDir = ""
			task = None
			
			jobName = self.request().field("editjob")
			self.session().setValue("jobpage_jobname", jobName)
			
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			jobDir = userDir+"/job_%s" % (jobName)
			
			taskFile = file(os.path.join(jobDir,"job.task"), "r")
			task = pickle.load(taskFile)
			task.refresh()
			taskFile.close()
			
			self.session().setValue("jobpage_task", task)
			self.session().setValue("jobpage_jobdir", jobDir)
			self.session().setValue("jobpage_editing", "")
			
			attribs = task.getAttributes()
			xrslAttribs = task.getXRSLAttributes()
			
			# Create the form, now with previous values
			
			self.onAssignFormValues(task, mainForm)
			
			# Change the submit button
			
			mainForm.addFormButton("Modify", "_action_modify")
			mainForm.addFormButton("Back", "_action_back")
			mainForm.setHaveSubmit(False)		
	
	def _writeContent(self):
		"""Render job page"""
		
		if self.session().hasValue("jobpage_status"):
		
			# -----------------------------------
			# Show any form messages
			# -----------------------------------
			
			if self.session().value("jobpage_status")<>"":
				Web.Dialogs.messageBox(self, self.session().value("jobpage_status"), "Message", self.session().value("jobpage_return_page"))

			self.session().delValue("jobpage_status")
			self.session().delValue("jobpage_return_page")
			
		elif self.session().hasValue("jobpage_message"):
			# -----------------------------------
			# Show any form messages
			# -----------------------------------
			
			if self.session().value("jobpage_message")<>"":
				Web.Dialogs.messageBox(self, self.session().value("jobpage_message"), "Message", self.onGetPageAddress())

			self.session().delValue("jobpage_message")
		else:
			
			# -----------------------------------
			# Create job form definition here 
			# -----------------------------------
			
			form = None
			
			if self.request().hasField("editjob"):
				# Ok. He wants to edit the job
				
				# Get neccessary info
				
				self.cleanSession()
				
				jobName = ""
				jobDir = ""
				task = None
				
				jobName = self.request().field("editjob")
				self.session().setValue("jobpage_jobname", jobName)
				
				user = Lap.Session.User(self.session().value('authenticated_user'))
				userDir = user.getDir();
				jobDir = userDir+"/job_%s" % (jobName)
				
				taskFile = file(os.path.join(jobDir,"job.task"), "r")
				task = pickle.load(taskFile)
				task.refresh()
				taskFile.close()
				
				self.session().setValue("jobpage_task", task)
				self.session().setValue("jobpage_jobdir", jobDir)
				self.session().setValue("jobpage_editing", "")
				
				attribs = task.getAttributes()
				xrslAttribs = task.getXRSLAttributes()
				
				# Create the form, now with previous values
				
				form = self.onCreateEditJobForm(task)
				
				# Change the submit button
				
				form.addFormButton("Modify", "_action_modify")
				form.addFormButton("Back", "_action_back")
				form.setHaveSubmit(False)
				
				self.__form = form				
				#self.session().setValue("jobpage_form", form)
				
			elif self.request().hasField("createjob"):
				
				# New job
				
				# Get default values from the task class
				
				self.cleanSession();
				
				task = self.onCreateNewTask()
				form = self.onCreateNewJobForm(task)
				form.setSubmitButton("_action_create", "Create")
				
				self.__form = form
				#self.session().setValue("jobpage_form", form)
				self.session().setValue("jobpage_task", task)				
				
			elif self.session().hasValue("jobpage_editing"):
			
				# Ok. He wants to edit the job
				
				# Get neccessary info
				
				jobName = ""
				jobDir = ""
				task = None
				
				sessionValid = True
				
				if not self.session().hasValue("jobpage_keep_edit"):
				
					jobName = self._getSessionValue("jobpage_jobname")
					
					if jobName == None:
						sessionValid = False
					else:
						user = Lap.Session.User(self.session().value('authenticated_user'))
						userDir = user.getDir();
						jobDir = userDir+"/job_%s" % (jobName)
						
						taskFile = file(os.path.join(jobDir,"job.task"), "r")
						task = pickle.load(taskFile)
						task.refresh()
						taskFile.close()
						
						self.session().setValue("jobpage_task", task)
						self.session().setValue("jobpage_jobname", jobName)
						self.session().setValue("jobpage_jobdir", jobDir)
	
						if self.session().hasValue("jobpage_keep_edit"):
							self.session().delValue("jobpage_keep_edit")
				else:
					
					task = self._getSessionValue("jobpage_task")
					jobName = self._getSessionValue("jobpage_jobname")
					jobDir = self._getSessionValue("jobpage_jobdir")
					
					if task == None or jobName == None or jobDir == None:
						sessionValid = False
				
				
				if sessionValid:
				
					attribs = task.getAttributes()
					xrslAttribs = task.getXRSLAttributes()
				
					# Create the form, now with previous values
				
					form = self.onCreateEditJobForm(task)
				
					# Change the submit button
				
					form.addFormButton("Modify", "_action_modify")
					form.addFormButton("Back", "_action_back")
					form.setHaveSubmit(False)
					
					self.__form = form			
					#self.session().setValue("jobpage_form", form)
					
				else:
					Web.Dialogs.infoBox(self, "Session invalid. try editing the job again." , "Information")
			

			if form!=None:
				form.render(self)
			
			# -----------------------------------
			# Show any form info messages
			# -----------------------------------
			
			if self.session().hasValue("jobpage_info"):
				if self.session().value("jobpage_info")<>"":
					Web.Dialogs.infoBox(self, self.session().value("jobpage_info"), "Information", form.getWidth())
				self.session().delValue("jobpage_info")
				
			
			
	def sleep(self, transaction):
		"""sleep() override to handle some session cleanup."""
		
		# Make sure that we don't edit the page all the time
		
		if not self.session().hasValue("jobpage_keep_edit"):
			if self.session().hasValue("editjob"):
				self.session().delValue("editjob")
			
		# Move along
			
		ApplicationSecurePage.sleep(self, transaction)
		
	def actions(self):
		"""Return the actions defined by this page.
		
		JobPage defines the actions, create, modify, back and uploadFile."""
		return ApplicationSecurePage.actions(self) + ["create", "modify", "back", "uploadFile"]		

	# ----------------------------------------------------------------------
	# Form action methods
	# ----------------------------------------------------------------------			

	def create(self):
		"""Handles the create action from a web request.
		
		This function creates a new job definition and stores
		the information on disk."""
	
		# -------------------------------------------
		# Get validated form fields (excl. files)
		# -------------------------------------------
		
		form = None
		
		if self.__form!=None:
			#if self.session().hasValue("jobpage_form"):
			#form = self.session().value("jobpage_form")
			form = self.__form
			form.retrieveFieldValues(self.request())
		else:
			self.setFormMessage("No form found.")
			self.writeBody()
			return

		error = None
		field = None
		returnPage = None
		
		error = self.onValidateValues(form)
		fieldValues = form.getFieldValues()
		
		if error!="":
			self.setFormStatus(error, returnPage)
			self.writeBody()		
			return

		# -------------------------------------------
		# Create job directory
		# -------------------------------------------
		
		jobName = fieldValues["jobName"]
		self.session().setValue("jobpage_jobname", jobName)

		user = Lap.Session.User(self.session().value('authenticated_user'))
		userDir = user.getDir();
		self.jobDir = userDir+"/job_%s" % (jobName)
		
		self.session().setValue("jobpage_jobdir", self.jobDir)

		try:
			os.mkdir(self.jobDir)
		except:
			pass

		# -------------------------------------------
		# Handle any file transfers here
		# -------------------------------------------
		
		fileTransferFields = self.onGetFileTransferFields()
		
		uploadedFiles = []
		
		for fileTransferField in fileTransferFields:
			uploadOk, filename = self._uploadFile(fileTransferField, self.jobDir)
			if uploadOk:
				uploadedFiles.append([filename, fileTransferField])

		# -------------------------------------------
		# Create task
		# -------------------------------------------
			
		task = self.onCreateNewTask()
		
		self.onAssignValues(task, form)
		
		for uploadedFile in uploadedFiles:
			self.onHandleUploadedFile(task, uploadedFile[0], uploadedFile[1])
		
		task.setDir(self.jobDir)
			
		task.setJobName(fieldValues["jobName"])

		if fieldValues.has_key("cpuTime"):
			task.setCpuTime(fieldValues["cpuTime"])

		if fieldValues.has_key("email"):
			task.setEmail(fieldValues["email"])
		
		task.setup()

		# Save the task for later reference

		taskFile = file(self.jobDir+"/job.task", "w")
		pickle.dump(task, taskFile)
		taskFile.close()
		
		lapInfo("%s, job definition created" % task.__class__)
			
		self.onJobCreated(task)

		if self.onEditAfterCreate():
			self.session().setValue("jobpage_editing", task.getJobName())
		else:
			self.setFormStatus("Job created successfully")
			
		self.session().setValue("jobpage_task", task)

		self.writeBody()
		

	def updateTask(self):
		"""Write current task to disk"""
		task = self.getTask()
		
		if task!=None:
		
			jobName = self.session().value("editjob")
		
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			jobDir = userDir+"/job_%s" % (jobName)

			taskFile = file(self.jobDir+"/job.task", "w")
			pickle.dump(task, taskFile)
			taskFile.close()
			

	def modify(self, confirmation = True):
		"""Handles the modify action of a form.
		
		Modifies existing job definition with the modified information
		obtained by the form."""
		
		# -------------------------------------------
		# Get validated form fields (excl. files)
		# -------------------------------------------
				
		form = None
		
		if self.__form!=None:
			#if self.session().hasValue("jobpage_form"):
			#form = self.session().value("jobpage_form")
			form = self.__form
			form.retrieveFieldValues(self.request())
		else:
			self.setFormMessage("No form found.")
			self.writeBody()
			return
		
		error = self.onValidateValues(form)
		fieldValues = form.getFieldValues()

		if error!="":
			self.session().setValue("editjob", fieldValues["jobName"])
			self.setFormInfo(error)
			self.writeBody()		
			return

		# -------------------------------------------
		# Get job directory
		# -------------------------------------------

		user = Lap.Session.User(self.session().value('authenticated_user'))
		userDir = user.getDir();
		
		jobName = self._getSessionValue("jobpage_jobname")
		if jobName == None:
			self.setFormMessage("Session invalid. Try editing the job again.")
			self.writeBody()
			return
		
		if fieldValues["jobName"]<>fieldValues["oldJobName"]:
			oldJobDir = os.path.join(userDir, "job_%s" % fieldValues["oldJobName"])
			newJobDir = os.path.join(userDir, "job_%s" % fieldValues["jobName"])
			try:
					os.rename(oldJobDir, newJobDir)
			except:
					lapWarning("Could not rename job, %s to %s" % (oldJobDir, newJobDir))
					
			self.session().setValue("jobpage_jobname", fieldValues["jobName"])
			jobName = fieldValues["jobName"]
		
		
		self.jobDir = userDir+"/job_%s" % (jobName)

		# -------------------------------------------
		# Handle any file transfers here
		# -------------------------------------------
		
		fileTransferFields = form.getFileTransferFields()
		
		uploadedFiles = []
		
		for fileTransferField in fileTransferFields:
			uploadOk, filename = self._uploadFile(fileTransferField, self.jobDir)
			if uploadOk:
				uploadedFiles.append([filename, fileTransferField])

		# -------------------------------------------
		# Load old task
		# -------------------------------------------

		task = self.getTask()
		
		if self.getTask()==None:
			taskFile = file(os.path.join(self.jobDir,"job.task"), "r")
			task = pickle.load(taskFile)
			taskFile.close()
		
		# If job was renamed the task definition must also be updated.

		task.setDir(self.jobDir)
		task.setJobName(jobName)

		self.onAssignValues(task, form)
		
		for uploadedFile in uploadedFiles:
			self.onHandleUploadedFile(task, uploadedFile[0], uploadedFile[1])

		task.refresh()
		task.setup()

		# Save the task for later reference

		taskFile = file(os.path.join(self.jobDir,"job.task"), "w")
		pickle.dump(task, taskFile)
		taskFile.close()
		
		self.session().setValue("jobpage_task", task)
		self.session().setValue("jobpage_jobname", task.getJobName())
		self.session().setValue("jobpage_jobdir", self.jobDir)

		if confirmation:
			self.onLeaveForm()
			self.setFormStatus("Job modified successfully", returnPage=self.request().adapterName()+"/ManageJobPage")
			
		self.writeBody()
		
	def back(self):
		"""Handles the back action of a form and returns to the ManageJobPage."""
		self.cleanSession()
		self.onLeaveForm()
		self.sendRedirectAndEnd(self.pageLoc()+"/ManageJobPage")
		

	def uploadFile(self):

		# -------------------------------------------
		# Get job directory
		# -------------------------------------------
		
		lapDebug("uploadFile: Get job directory.")

		user = Lap.Session.User(self.session().value('authenticated_user'))
		userDir = user.getDir();
		
		# -------------------------------------------
		# Get validated form fields (excl. files)
		# -------------------------------------------

		lapDebug("uploadFile: Get validated fields")
		
		form = None
		task = None
		
		if self.session().hasValue("jobpage_form"):
			#if self.session().hasValue("jobpage_form"):
			#form = self.session().value("jobpage_form")
			form = self.__form
			form.retrieveFieldValues(self.request())

		if self.session().hasValue("jobpage_task"):
			task = self.session().value("jobpage_task")
				
		self.jobDir = userDir+"/job_%s" % (task.getJobName())
		
		# -------------------------------------------
		# Does the upload depend on any form values?
		# -------------------------------------------
		
		if self.onHandleFormValuesOnUpload():
			
			error = self.onValidateValuesUpload(form)
			fieldValues = form.getFieldValues()
	
			if error!="":
				self.session().setValue("editjob", fieldValues["jobName"])
				self.setFormInfo(error)
				self.writeBody()		
				return
		
		# -------------------------------------------
		# Handle any file transfers here
		# -------------------------------------------
		
		lapDebug("uploadFile: Handle file uploads.")
		fileTransferFields = form.getFileTransferFields()
		
		uploadedFiles = []
		
		for fileTransferField in fileTransferFields:
			uploadOk, filename = self._uploadFile(fileTransferField, self.jobDir)
			if uploadOk:
				uploadedFiles.append([filename, fileTransferField])
			
		# -------------------------------------------
		# Load old task
		# -------------------------------------------
		
		taskFile = file(os.path.join(self.jobDir,"job.task"), "r")
		task = pickle.load(taskFile)
		taskFile.close()
		
		if self.onHandleFormValuesOnUpload():
			self.onAssignValuesUpload(task, form)		

		lapDebug("uploadFile: onHandleUploadedFile()")

		for uploadedFile in uploadedFiles:
			lapInfo("Handling uploaded file: %s, %s" % (uploadedFile[0], uploadedFile[1]))
			self.onHandleUploadedFile(task, uploadedFile[0], uploadedFile[1])
			
		lapDebug("uploadFile: Update task.")
		
		task.setup()

		# Save the task for later reference

		lapDebug("uploadFile: Saving task")

		taskFile = file(os.path.join(self.jobDir,"job.task"), "w")
		pickle.dump(task, taskFile)
		taskFile.close()
		
		self.session().setValue("jobpage_task", task)
		self.session().setValue("jobpage_jobname", task.getJobName())
		self.session().setValue("jobpage_jobdir", self.jobDir)		
		
		self.session().setValue("editjob", task.getJobName())
		self.writeBody()		
		
	# ----------------------------------------------------------------------
	# JobPage Event methods (Callbacks)
	# ----------------------------------------------------------------------
	
	def onAssignFormValues(self, task, form):
		pass

	def onCreateNewTask(self):
		"""Return the task instance for derived JobPage class.
		
		This method is called when a new instance of a task is needed,
		for example when a new job definition is created. (Must implement)"""
		pass
	
	def onCreateNewJobForm(self, task=None):
		"""Return form used when creating a new job definition.
		
		The JobPage class provides a default job creation form asking
		for the name of the new job definition. (Optional)"""
		
		form = Web.UiExt.Form(self, "newJobForm")
		form.caption = "Create an %s job" % (task.getDescription())
		
		attribs = task.getAttributes()
		xrslAttribs = task.getXRSLAttributes()
		
		jobName = Web.UiExt.TextField(self, "jobName", "Job name")
		jobName.value = xrslAttribs["jobName"]
		
		form.add(jobName)
	
		return form
	
	def onCreateEditJobForm(self, task=None):
		"""Return form used when editing an existing job definition.
		
		This method is called when an editing form is needed for editing
		an existing job definition. (Must implement)"""
		pass
	
	def onValidateValues(self, form):
		"""Validate form input values.
		
		This method is called when the form input is validated, in response
		to a create or modify action. The values can be modified silently
		or with an error. To raise an validation error return a non-empty
		string. (Optional)"""
		return (None)

	def onAssignValues(self, task, form):
		"""Assign form input to task attributes.
		
		This method is called when the task attributes are updated
		or changed. The form values can be considered validated at this
		stage. To raise an validation error return a non-empty
		string. (Must implement)"""
		return (None)

	def onValidateValuesUpload(self, form):
		"""Assign form input to task attributes for upload action.
		
		This method is called when the task attributes are updated
		or changed. The form values can be considered validated at this
		stage. To raise an validation error return a non-empty
		string. (Optional)"""
		return self.onValidateValues(form)

	def onAssignValuesUpload(self, task, form):
		"""Validate form input values for upload action.
		
		This method is called when the form input is validated, in response
		to a create or modify action. The values can be modified silently
		or with an error. To raise an validation error return a non-empty
		string. (Must implement)"""
		return self.onAssignValues(task, form)

	def onHandleUploadedFile(self, task, filename, fieldname):
		"""Special handling for uploaded files.
		
		This method is called for each uploaded file. This can be used
		to assign, add or modify files for the current task. The, task,
		parameter contains the current task, the filename contains the
		filename of the newly uploaded file and fieldname contains the
		name of the upload field in the form instance. (Optional)"""
		pass
	
	def onGetPageAddress(self):
		"""Return the location of the derived page.
		
		A typical return value can be:
		
		return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
		
		(Must implement)"""
		return "JobPage"
	
	def onGetFileTransferFields(self):
		"""Return list of file transfer fields in the form.
		
		This method is called to determine which fields in the
		form that are file transfer fields. (Must implement)"""
		return []
	
	def onReturnPageName(self):
		"""Return the page to return after editing. (Optional, default=ManageJobPage)"""
		return "ManageJobPage"
	
	def onJobCreated(self, task):
		"""Job created event method.
		
		This method is called when a new job definition has been created. (Optional)"""
		pass
	
	def onEditAfterCreate(self):
		"""Return True if the job editing form is to be shown after job creation.
		(Optional, default=False)"""
		return False
	
	def onLeaveForm(self):
		"""Form leave event method.
		
		This method is called when the user is leaving the form. (Optional)"""
		pass
	
	def onHandleFormValuesOnUpload(self):
		"""Return True if form values is to be considered when uploading files. (Optional)"""
		return False
	
	# ----------------------------------------------------------------------
	# Obsolete methods
	# ----------------------------------------------------------------------			

	def onValidate(self, request):
		return (None, None, None)
	
	def onValidateCreate(self, request):
		return (None, None, None)

	def onValidateModify(self, request):
		return (None, None, None)

	def onValidateUpload(self, request):
		return (None, None, None)

	def onAssignAttribs(self, task, field, request):
		pass	

	def onHandleFileTransfers(self, request, destDir):
		pass

	def setReturnPage(self, returnPage):
		self._returnPage = self.pageLoc()+"/" % returnPage
