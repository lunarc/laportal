from Web.ApplicationSecurePage import ApplicationSecurePage
from time import *

import os
import sys
import pwd
import string
import pickle

from HyperText.HTML import *

import Grid.ARC
import Lap.Session
import Web.Ui
import Web.Dialogs

class ManageGridJobPage(ApplicationSecurePage):
	
	def statusImage(self, status):
		
		if status == "ACCEPTING" or status=="ACCEPTED":
			return "images/stat_accepted.gif"
		if status == "PREPARING" or status=="PREPARED":
			return "images/stat_preparing.gif"
		if status == "INLRMS:Q":
			return "images/stat_inlrms_q.gif"
		if status == "INLRMS:R" or status == "INLRMS:S" or status=="INLRMS:E" or status=="INLRMS:O":
			return "images/stat_inlrms_r.gif"
		if status == "FINISHING":
			return "images/stat_finishing.gif"
		if status == "EXECUTED":
			return "images/stat_inlrms_r.gif"
		if status == "FINISHED":
			return "images/stat_finished.gif"
		if status == "DELETED":
			return "images/stat_deleted.gif"
		if status == "FAILED" or status == "KILLED":
			return "images/stat_failed.gif"
		return "images/stat_finished.gif"

	def writeHead(self):
	
		if self.session().hasValue("grid_job_metarefresh"):
			self.writeln("""<META HTTP-EQUIV="REFRESH" CONTENT="0;ManageGridJobPage">""")
			self.session().delValue("grid_job_metarefresh")
		else:
			self.writeln('<meta http-equiv="refresh" content=300>')

		ApplicationSecurePage.writeHead(self)


	def writeContent(self):
		
		if self.session().hasValue("grid_job_status"):

			# Show any form message boxes
			
			if self.session().value("grid_job_status")<>"":
				Web.Dialogs.messageBox(self, self.session().value("grid_job_status"), "Message", "ManageGridJobPage", width="30em")

			self.session().delValue("grid_job_status")

		elif self.session().hasValue("grid_job_wait"):

			message = self.session().value("grid_job_wait")
			self.session().delValue("grid_job_wait")

			Web.Dialogs.pleaseWaitBox(self, message)
			
		else:
			
			# Handle page requests
			
			viewMode = self.getString(self.request(), "viewMode")
			viewJobIndex = self.getInt(self.request(), "jobIndex")
			
			# Get user information
		
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			# Get the ARC user interface
			
			ui = Grid.ARC.Ui(user)
			
			# Get a job status list

			jobs = None
			
			if self.session().hasValue("grid_job_cacheJobList"):
				self.session().delValue("grid_job_cacheJobList")
				if self.session().hasValue("grid_job_jobs"):
					jobs = self.session().value("grid_job_jobs")
				else:
					jobs = ui.jobStatusArclib()
					self.session().setValue("grid_job_jobs", jobs)
			else:
				jobs = ui.jobStatus()
				self.session().setValue("grid_job_jobs", jobs)
				
			print "jobs = ", jobs

			if jobs==None:
				
				Web.Dialogs.messageBox(self, "grid-proxy is about to expire please create a new proxy.", "Manage running jobs")
			
			elif len(jobs)==0:
				
				# No job dirs exists => no jobs to manage
				
				Web.Dialogs.messageBox(self, "No jobs to manage", "Get jobs")
				
			else:
				
				# Create javascript for popping up output window.
				# When doing this a cached job list is used to
				# prevent an extra ngstat -a from occuring
				
				keyList = jobs.keys()
				
				if viewMode!=None:
					self.showOutputWindow(keyList[viewJobIndex], "", viewMode)

				# Create form for managing jobs
				
				form = Web.Ui.TableForm("frmJobManager", "", "Manage GRID jobs", "55em", len(jobs)+1, 10)
				
				form.setAction("ManageGridJobPage")
				
				row = 0
				
				form.addNormalText("", row, 0)
				form.addNormalText(B("JobID"), row, 1)
				form.addNormalText("", row, 2)
				form.addNormalText(B("JobName"), row, 3)
				form.addNormalText("", row, 4)
				form.addNormalText("", row, 5)
				form.addNormalText("", row, 6)
				form.addNormalText("", row, 7)
				form.addNormalText(B("Status"), row, 8)
				form.addNormalText("", row, 9)
				
				row = row + 1
				
				for key in jobs.keys():
					print key
					if jobs[key].has_key("name"):
						form.addCheck("", "chkJob", "%s;%s" % (jobs[key]["name"],key), row, 0)
						form.addNormalText(key, row, 1)
						form.addNormalText("", row, 2)
						form.addNormalText(jobs[key]["name"], row, 3)
						form.addNormalText("", row, 4)
						form.addNormalText(A(IMG(src="images/file_view.gif", border=0),href="ManageGridJobPage?viewMode=stdout&jobIndex="+str(row-1)), row, 5)
						form.addNormalText(A(IMG(src="images/output_error.gif", border=0),href="ManageGridJobPage?viewMode=stderr&jobIndex="+str(row-1)), row, 6)
						form.addNormalText(A(IMG(src="images/output_log.gif", border=0),href="ManageGridJobPage?viewMode=gridlog&jobIndex="+str(row-1)), row, 7)
						form.addNormalText(B(jobs[key]["status"]), row, 8)
						form.addNormalText(IMG(src=self.statusImage(jobs[key]["status"])), row, 9)
					
						row = row + 1
					else:
						form.addRadio("", "chkJob", "%s;%s" % ("NONAME",key), row, 0)
						form.addNormalText(key, row, 1)
						form.addNormalText("", row, 2)
						form.addNormalText("NONAME", row, 3)
						form.addNormalText("", row, 4)
						form.addNormalText(A(IMG(src="images/file_view.gif", border=0),href=""), row, 5)
						form.addNormalText(A(IMG(src="images/output_error.gif", border=0),href=""), row, 6)
						form.addNormalText(A(IMG(src="images/output_log.gif", border=0),href=""), row, 7)
						form.addNormalText(B(jobs[key]["status"]), row, 8)
						form.addNormalText(IMG(src=self.statusImage(jobs[key]["status"])), row, 9)
					
						row = row + 1
						
					
				form.addFormButton("Get", "_action_getJob")
				form.addFormButton("Kill", "_action_killJob")
				form.addFormButton("Clean", "_action_cleanJob")
				form.addFormSpacer("10px")
				#form.addFormButton("Output", "_action_showStandardOutput")
				#form.addFormButton("Errors", "_action_showStandardError")
				#form.addFormButton("Log", "_action_showGridLog")
				form.addFormSpacer("10px")
				form.addFormButton("Refresh", "_action_refreshList")
				
				form.setHaveSubmit(False)
					
				form.render(self)
			
	def getJob(self):
		
		if self.request().hasValue("chkJob"):
			
			jobList = []
			
			chkJob = self.request().field("chkJob")
			
			# Check for single or multiple selection
			
			if type(chkJob) is str:
				jobName, jobId = chkJob.split(";")
				jobList.append([jobName, jobId])
			else:
				for job in chkJob:
					jobName, jobId = job.split(";")
					jobList.append([jobName, jobId])
					
			print jobList
					
			# Loop over job list to retrieve selected jobs
			
			self.pleaseWait("Downloading job(s)...")

			messages = ""
			
			for job in jobList:
				
				# Get selected jobname

				jobName = job[0]
				jobId = job[1]
				
				print "jobName", job[0]
				print "jobId", job[1]
			
				# Get user dir
		
				user = Lap.Session.User(self.session().value('authenticated_user'))
				userDir = user.getDir();
				ui = Grid.ARC.Ui(user)
				
				# Is it a multiple job
				
				baseJobName = ""
				subJobName = ""
				
				if jobName.find("_multiple")!=-1:
					(baseJobName, subJobName, suffix) = jobName.split("_")
					print baseJobName, ", ", subJobName, ", ", suffix
					downloadDir = os.path.join(userDir, "job_%s" % baseJobName)
				else:
					downloadDir = os.path.join(userDir, "job_%s" % jobName)
				try:
					os.mkdir(downloadDir)
				except:
					pass
				
				if subJobName=="":
					result = ui.get(jobId, downloadDir)
				else:
					result = ui.get(jobId, downloadDir, subJobName)				
				
				if result==0:
					messages = messages + "Results for " + jobName + " downloaded to job directory.<br>"
				else:
					messages = messages + "Results for " + jobName + " failed to download.<br>"
					
			self.setFormStatus(messages)
			
		else:
			self.setFormStatus("No jobs selected.")
			self.cacheJobList()
		
		
	def killJob(self):

		if self.request().hasValue("chkJob"):
			
			jobList = []
			
			chkJob = self.request().field("chkJob")
			
			# Check for single or multiple selection
			
			if type(chkJob) is str:
				jobName, jobId = chkJob.split(";")
				jobList.append([jobName, jobId])
			else:
				for job in chkJob:
					jobName, jobId = job.split(";")
					jobList.append([jobName, jobId])
					
			print jobList
					
			# Loop over job list to kill them
			
			self.pleaseWait("Killing job(s)...")

			messages = ""
			
			for job in jobList:
				
				# Get selected jobname

				jobName = job[0]
				jobId = job[1]
				
				print "jobName", job[0]
				print "jobId", job[1]
			
				# Get user dir
		
				user = Lap.Session.User(self.session().value('authenticated_user'))
				userDir = user.getDir();
				ui = Grid.ARC.Ui(user)
				
				result = ui.kill(jobId)
												
				if result==0:
					messages = messages + "Job " + jobName + " killed.<br>"
				else:
					messages = messages + "Job " + jobName + " could not be killed.<br>"
					
			self.setFormStatus(messages)
			self.refreshJobList()			
		else:
			self.setFormStatus("No jobs selected.")
			self.cacheJobList()
				
	def cleanJob(self):

		if self.request().hasValue("chkJob"):
			
			jobList = []
			
			chkJob = self.request().field("chkJob")
			
			# Check for single or multiple selection
			
			if type(chkJob) is str:
				jobName, jobId = chkJob.split(";")
				jobList.append([jobName, jobId])
			else:
				for job in chkJob:
					jobName, jobId = job.split(";")
					jobList.append([jobName, jobId])
					
			print jobList
					
			# Loop over job list to clean them
			
			self.pleaseWait("Cleaning job(s)...")

			messages = ""
			
			for job in jobList:
				
				# Get selected jobname

				jobName = job[0]
				jobId = job[1]
				
				print "jobName", job[0]
				print "jobId", job[1]
			
				# Get user dir
		
				user = Lap.Session.User(self.session().value('authenticated_user'))
				userDir = user.getDir();
				ui = Grid.ARC.Ui(user)
				
				result = ui.clean(jobId)
												
				if result==0:
					messages = messages + "Job " + jobName + " cleaned.<br>"
				else:
					messages = messages + "Job " + jobName + " could not be cleaned.<br>"
					
			self.setFormStatus(messages)
			self.refreshJobList()
		else:
			self.setFormStatus("No jobs selected.")
			self.cacheJobList()
			
	def setFormStatus(self, status):
		self.session().setValue("grid_job_status", status)

	def pleaseWait(self, message):
		self.session().setValue("grid_job_wait", message)
		self.session().setValue("grid_job_metarefresh", "")
		self.writeHead()
		self.writeBody()
		self.response().flush()
		
	def refreshList(self):
		self.writeBody()
		
	def showOutputWindow(self, jobId, jobName, outputType="stdout"):
		self.session().setValue("viewOutput_jobId", jobId)
		self.session().setValue("viewOutput_jobName", jobName)
		self.session().setValue("viewOutput_type", outputType)
		self.writeln('<script language="javascript">')
		self.writeln('<!--')
		self.writeln('viewOutputWindow = window.open("ViewOutputPage", "viewOutputWindow", config="height=800,width=600, toolbar=yes, menubar=no, scrollbars=yes, resizable=yes, location=no, status=no")')
		self.writeln('if (viewOutputWindow.focus) {viewOutputWindow.focus()}')
		self.writeln('-->')
		self.writeln('</script>')
		self.cacheJobList()
		
	def cacheJobList(self):
		self.session().setValue("grid_job_cacheJobList", "")
		
	def refreshJobList(self):
		self.session().delValue("grid_job_cacheJobList")
		
		
	def actions(self):
		return ApplicationSecurePage.actions(self) + ["getJob",
			 "killJob",
			 "cleanJob",
			 "refreshList"]
