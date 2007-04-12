from Web.ApplicationSecurePage import ApplicationSecurePage

from time import *
import os, sys, pwd, string, pickle, shutil, time

from HyperText.HTML import *

import Grid.ARC

import Lap
import Lap.Session
from Lap.Log import *

import Web
import Web.Ui
import Web.Dialogs

class ManageJobPage(ApplicationSecurePage):

	def writeHead(self):

		if self.session().hasValue("managejob_metarefresh"):
			
			self.writeln("""<META HTTP-EQUIV="REFRESH" CONTENT="0;ManageJobPage">""")
			self.session().delValue("managejob_metarefresh")

		ApplicationSecurePage.writeHead(self)

	def writeContent(self):
		
		if self.session().hasValue("managejob_status"):

			# Show any form message boxes
			
			if self.session().value("managejob_status")<>"":
				Web.Dialogs.messageBox(self, self.session().value("managejob_status"), "Message", "ManageJobPage", width="30em")

			self.session().delValue("managejob_status")

		elif self.session().hasValue("managejob_wait"):

			message = self.session().value("managejob_wait")
			self.session().delValue("managejob_wait")

			Web.Dialogs.pleaseWaitBox(self, message)			
			
		elif self.session().hasValue("managejob_confirm"):
			
			# Show form confirmation dialogs
			
			Web.Dialogs.messageBoxYesNo(self,
								self.session().value("managejob_confirm"),
								self.session().value("managejob_confirm_title"),
								"_action_deleteJobYes",
								"_action_deleteJobNo"
								)
			
			self.session().delValue("managejob_confirm")
			self.session().delValue("managejob_confirm_title")
			self.session().delValue("managejob_confirm_no_page")
			self.session().delValue("managejob_confirm_yes_page")
			
		else:		
		
			wl = self.writeln
			w = self.write
			
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			# Check for job directories in user dir
			
			jobCount = 0
			jobs = []
			
			for entry in os.listdir(userDir):
				if os.path.isdir(os.path.join(userDir,entry)):
					if entry[0:4] == "job_":
						jobName = entry[4:]
						jobCount = jobCount + 1
						
						# Get job description
						
						jobDir = os.path.join(userDir, entry)
						taskFilename = os.path.join(jobDir, "job.task")
						
						if os.path.exists(taskFilename):
						
							taskFile = file(taskFilename, "r")
							task = pickle.load(taskFile)				
							taskFile.close()
						
							jobs.append([jobName, task.getDescription(), task.getTaskEditPage()])

						
			if len(jobs)==0:
				
				# No job dirs exists => no jobs to manage
				
				Web.Dialogs.messageBox(self, "No jobs to manage", "Manage jobs")
			else:
				
				# Create form for managing jobs
				
				print "request = ", self.request()
				
				form = Web.Ui.TableForm("frmJobManager", "", "Manage job definitions", "26em", len(jobs)+1, 5)
				
				form.setAction("ManageJobPage")
				
				row = 0
				
				form.addNormalText("", row, 0)
				form.addNormalText(B("Jobname"), row, 1)
				form.addNormalText(B("Type"), row, 2)
				form.addNormalText("", row, 3)
				form.addNormalText("", row, 4)
				
				row = row + 1
				
				for job in jobs:
					form.addCheck("", "chkJob", job[0], row, 0)
					form.addNormalText(job[0], row, 1)
					form.addNormalText(job[1], row, 2)
					form.addNormalText(A(IMG(src="images/edit.gif", border=0), href=self.pageLoc()+job[2]+"?editjob="+job[0]), row, 3)
					form.addNormalText(A(IMG(src="images/folder.gif", border=0), href="ViewFilesPage?mode=session&jobname="+job[0]), row, 4)
					row = row + 1
					
				form.addFormButton("Submit", "_action_submitJob")	
				form.addFormButton("Delete", "_action_deleteJob")
				
				form.setHaveSubmit(False)
					
				form.render(self)
			
	def editJob(self):
		
		if self.request().hasValue("chkJob"):
			
			# Get selected jobname
			
			jobName = self.getString(self.request(),"chkJob")
			
			# Get user dir
			
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			# Set session variable edit job to tell the job page
			# that we want to edit the job instead of creating and
			# assign the job name as value

			self.session().setValue("editjob", jobName)
			
			jobDir = os.path.join(userDir, "job_%s" % jobName)
			
			# Read the job task 
			
			taskFile = file(os.path.join(jobDir,"job.task"), "r")
			task = pickle.load(taskFile)
			taskFile.close()
			
			# Forward to the requested edit page
			
			self.forward(task.getTaskEditPage())
		else:
			self.setFormStatus("A job must be selected.")
			self.writeBody()
		
		
	def viewJobFiles(self):
		
		print "request = ", self.request().fields()		

		if self.request().hasValue("chkJob"):
			
			# Get selected jobname
			
			jobName = self.getString(self.request(),"chkJob")
			
			# Get user dir
			
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			self.session().setValue("ViewFilesPage_mode", "session")
			self.session().setValue("ViewFilesPage_jobname", jobName)
					
			self.forward("ViewFilesPage")

		else:
			self.setFormStatus("A job must be selected.")
			self.writeBody()
	
	def submitJob(self):

		if self.request().hasValue("chkJob"):
			
			# Get user dir
			
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();

			# Get selected jobname
			
			jobNames = self.request().field("chkJob")
			
			jobNameList = []
			
			if type(jobNames) is str:
				jobNameList.append(jobNames)
			else:
				jobNameList = jobNames
				
			self.pleaseWait("Submitting job(s)...")
			
			submittedJobIds = []
			
			# Submit all selected jobs

			for jobName in jobNameList:
			
				jobDir = os.path.join(userDir, "job_%s" % jobName)			
				
				# Read the job task 
				
				taskFile = file(os.path.join(jobDir,"job.task"), "r")
				task = pickle.load(taskFile)
				taskFile.close()
				
				ARC = Grid.ARC.Ui(user)
				resultVal, jobIds = ARC.submit(os.path.join(jobDir,"job.xrsl"))
				
				if len(jobIds)>0:
					for jobId in jobIds:
						submittedJobIds.append(jobId)
	
			if len(submittedJobIds)>0:
				message = "Submitted the following job(s):<br><br>"
				for jobId in submittedJobIds:
					lapInfo("Job %s submitted." % jobId)
					message = message + jobId + "<br>"
			else:
				lapWarning("Job(s) could not be submitted.")
				message = "Could not find any resources to submit the job."

			self.setFormStatus(message)
		else:
			self.setFormStatus("A job must be selected.")
			self.writeBody()
			
	def deleteJob(self):
		if self.request().hasValue("chkJob"):
			self.confirm("Are you sure?", "Delete job", "", "")
			self.session().setValue("managejob_deletejob", self.getString(self.request(),"chkJob"))
			self.writeBody()
		else:
			self.setFormStatus("A job must be selected.")
			self.writeBody()
		
	def deleteJobYes(self):
		
		if self.session().hasValue("managejob_deletejob"):
			
			jobNames = self.session().value("managejob_deletejob")

			# Get user dir

			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			self.session().delValue("managejob_deletejob")
			
			if type(jobNames) is str:
				
				print "Deleting single job", jobNames
				
				if jobNames == "":
					return
				
				jobDir = os.path.join(userDir, "job_%s" % jobNames)
			
				# Delete job directory
			
				shutil.rmtree(jobDir, True)
			
			else:
			
				if len(jobNames) == 0:
					return
			
				print "Deleting jobNames =", jobNames
			
				for jobName in jobNames:
					
					print jobName
				
					jobDir = os.path.join(userDir, "job_%s" % jobName)
				
					# Delete job directory
				
					shutil.rmtree(jobDir, True)
				
			self.writeBody()
			
			
	def deleteJobNo(self):
		if self.session().hasValue("managejob_deletejob"):
			self.session().delValue("managejob_deletejob")
		self.writeBody()
	
	def setFormStatus(self, status):
		self.session().setValue("managejob_status", status)

	def pleaseWait(self, message):
		self.session().setValue("managejob_wait", message)
		self.session().setValue("managejob_metarefresh", "")
		self.writeHead()
		self.writeBody()
		self.response().flush()

		
	def confirm(self, question, title, yesPage, noPage):
		self.session().setValue("managejob_confirm", question)
		self.session().setValue("managejob_confirm_title", title)
		self.session().setValue("managejob_confirm_yes_page", yesPage)
		self.session().setValue("managejob_confirm_no_page", noPage)
	
	def actions(self):
		return ApplicationSecurePage.actions(self) + ["submitJob",
			 "deleteJob",
			 "deleteJobYes",
			 "deleteJobNo"]
