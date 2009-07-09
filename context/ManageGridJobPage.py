#
# ManageGridJobPage
#
# Copyright (C) 2006-2009 Jonas Lindemann
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

"""ManageGridJobPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

from time import *
import os, sys, pwd, string, pickle, random, md5, time

from HyperText.HTML import *

import Lap.Session
import Web.Ui
import Web.Dialogs

class ManageGridJobPage(ApplicationSecurePage):
    """Page for managing grid jobs.
    
    Displays a list of all running and non-running grid-jobs with options
    for killing, cleaning and viewing job output."""
    
    def statusImage(self, status):
        
        if status == "ACCEPTING" or status=="ACCEPTED":
            return "images/stat_accepted.gif"
        if status == "PREPARING" or status=="PREPARED":
            return "images/stat_preparing.gif"
        if status == "INLRMS: Q":
            return "images/stat_inlrms_q.gif"
        if status == "INLRMS: R" or status == "INLRMS: S" or status=="INLRMS: E" or status=="INLRMS: O":
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
    
    def onInitPage(self):
        """
        Init JavaScript controls for the job table.
        """
        
        self._form = Web.Ui.TableForm("frmJobManager", "", "Manage GRID jobs", "100%", 5, 5)
        self._form.page = self
        self._form.sortColumn = 1
        self._form.sortType = "asc"
        
        self.addControl(self._form)

    def writeContent(self):
        """
        Render page HTML.
        """
        
        if self.session().hasValue("grid_job_status"):

            # Show any form message boxes
            
            if self.session().value("grid_job_status")<>"":
                Web.Dialogs.messageBox(self, self.session().value("grid_job_status"), "Message", "ManageGridJobPage", width="30em", showOk=True)
            self.session().delValue("grid_job_status")
            
        else:
            
            # Handle page requests
            
            viewMode = self.getString(self.request(), "viewMode")
            viewJobIndex = self.getInt(self.request(), "jobIndex")
            
            # Get user information
        
            user = Lap.Session.User(self.session().value('authenticated_user'))
            userDir = user.getDir();
            
            # Create a list of jobs from arcClient
            
            jobs = self.createJobList()
                
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
                
                self._form.clear()
                self._form.action = "ManageGridJobPage"
                self._form.rows = len(jobs)
                
                row = 0
                
                #self._form.headers = ["Select", "Job id", "Job name", "", "Status", "", "", ""]
                self._form.headers = ["Select", "Job id", "Job name", "", "Status"]
                                
                for key in jobs.keys():
                    if jobs[key].has_key("name"):
                        self._form.addCheck("", "chkJob", "%s;%s" % (jobs[key]["name"],key), row, 0)
                        self._form.addNormalText(key, row, 1)
                        self._form.addNormalText(jobs[key]["name"], row, 2)
                        self._form.addNormalText(IMG(src=self.statusImage(jobs[key]["status"])), row, 3)
                        self._form.addNormalText(B(jobs[key]["status"]), row, 4)
                        #self._form.addNormalText(A(IMG(src="images/file_view.gif", border=0),href="ManageGridJobPage?viewMode=stdout&jobIndex="+str(row-1)), row, 5)
                        #self._form.addNormalText(A(IMG(src="images/output_error.gif", border=0),href="ManageGridJobPage?viewMode=stderr&jobIndex="+str(row-1)), row, 6)
                        #self._form.addNormalText(A(IMG(src="images/output_log.gif", border=0),href="ManageGridJobPage?viewMode=gridlog&jobIndex="+str(row-1)), row, 7)
                    
                        row = row + 1
                    else:
                        self._form.addCheck("", "chkJob", "%s;%s" % ("NONAME",key), row, 0)
                        self._form.addNormalText(key, row, 1)
                        self._form.addNormalText("NONAME", row, 2)
                        self._form.addNormalText(IMG(src=self.statusImage(jobs[key]["status"])), row, 3)
                        self._form.addNormalText(B(jobs[key]["status"]), row, 4)
                        #self._form.addNormalText(A(IMG(src="images/file_view.gif", border=0),href="ManageGridJobPage?viewMode=stdout&jobIndex="+str(row-1)), row, 5)
                        #self._form.addNormalText(A(IMG(src="images/output_error.gif", border=0),href="ManageGridJobPage?viewMode=stderr&jobIndex="+str(row-1)), row, 6)
                        #self._form.addNormalText(A(IMG(src="images/output_log.gif", border=0),href="ManageGridJobPage?viewMode=gridlog&jobIndex="+str(row-1)), row, 7)
                    
                        row = row + 1
                        
                    
                self._form.addFormButton("Get", "_action_getJob")
                self._form.addFormButton("Kill", "_action_killJob")
                self._form.addFormButton("Clean", "_action_cleanJob")
                self._form.addFormButton("Query Status", "_action_queryGrid")
                #self._form.addFormButton("Output", "_action_showStandardOutput")
                #self._form.addFormButton("Errors", "_action_showStandardError")
                #self._form.addFormButton("Log", "_action_showGridLog")
                
                self._form.haveSubmit = False
                    
                self._form.render(self)
                
    def uuid(self,  *args ):
        """
          Generates a universally unique ID.
          Any arguments only create more randomness.
        """
        t = long( time.time() * 1000 )
        r = long( random.random()*100000000000000000L )
        a = random.random()*100000000000000000L
        data = str(t)+' '+str(r)+' '+str(a)+' '+str(args)
        data = md5.md5(data).hexdigest()
        return data

    def createJobList(self):
        
        jobs = {}
        
        for jobId in self.arcClient.jobDict.keys():
            jobName = self.arcClient.jobDict[jobId]["Name"]
            if self.arcClient.jobDict[jobId].has_key("State"):
                jobStatus = self.arcClient.jobDict[jobId]["State"]
            else:
                jobStatus = "Unknown"
            
            jobError = ""
            jobs[jobId] = {"name": jobName, "status": jobStatus, "error": jobError}
            
        return jobs
                
    def createFakeJobList(self, jobSize):
        n = range(jobSize)
        
        jobs = {}
        
        hosts = ["siri.lunarc.lu.se", "milleotto-grid.lunarc.lu.se", "grad.uppmax.uu.se"]
        status = ["ACCEPTING", "ACCEPTED", "PREPARING", "PREPARED", "INLRMS:Q", "INLRMS:R", "INLRMS:S", "INLRMS:E", "INLRMS:O", "FINISHING", "EXECUTED", "FINISHED", "DELETED", "FAILED"]
        names = ["Python_001", "Matlab_002", "ABAQUS_004"]
        for i in n:
            hostname = random.choice(hosts)
            uuid = self.uuid()
            jobId = "gsiftp://%s/%s" % (hostname, uuid)
            jobName = random.choice(names)
            jobStatus = random.choice(status)
            jobError = ""
            jobs[jobId] = {"name": jobName, "status": jobStatus, "error": jobError}
            
        return jobs
    
    def getJob(self):
        """
        Retrieve selected jobs from grid (action).
        """
        
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
                                       
            # Loop over job list to retrieve selected jobs
            
            messages = ""
            
            for job in jobList:
                
                # Get selected jobname

                jobName = job[0]
                jobId = job[1]
                            
                # Get user dir
        
                user = Lap.Session.User(self.session().value('authenticated_user'))
                userDir = user.getDir()
                
                # Determine where to put the job output files.
                
                baseName = jobName.split("_")[0]
                taskId = jobName.split("_")[1]
                
                jobDir = os.path.join(userDir, "job_%s" % baseName)
                taskDir = os.path.join(jobDir, "%s_%s" % (baseName, taskId))
                
                if os.path.exists(jobDir) and os.path.exists(taskDir):
                    
                    # Download job,

                    self.arcClient.downloadDir = taskDir
                    self.arcClient.get([jobId])
                    self.writeBody()
                else:
                    self.setFormStatus("Job definition or task dir has been removed.")
                    self.writeBody()
        else:
            self.setFormStatus("No jobs selected.")
            self.writeBody()
        
    def killJob(self):
        """
        Kill selected running jobs (action).
        """

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
                                        
            # Loop over job list to kill them
            
            self.pleaseWait("Killing job(s)...")

            messages = ""
            
            for job in jobList:
                
                # Get selected jobname

                jobName = job[0]
                jobId = job[1]
                            
                # Get user dir
        
                user = Lap.Session.User(self.session().value('authenticated_user'))
                userDir = user.getDir();
                
                self.arcClient.kill([jobId])
                self.arcClient.loadJobList()
                    
            self.writeBody()
            
        else:
            self.setFormStatus("No jobs selected.")
            self.writeBody()
                
    def cleanJob(self):
        """
        Clean selected jobs.
        """

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
                                        
            # Loop over job list to clean them
            
            messages = ""
            
            for job in jobList:
                
                # Get selected jobname

                jobName = job[0]
                jobId = job[1]
                            
                # Get user dir
        
                user = Lap.Session.User(self.session().value('authenticated_user'))
                userDir = user.getDir();
                
                self.arcClient.clean([jobId])
                self.arcClient.loadJobList()
                
            self.writeBody()
        else:
            self.setFormStatus("No jobs selected.")
            self.writeBody()
            
    def setFormStatus(self, status):
        """
        Set the message to display form status.
        """

        self.session().setValue("grid_job_status", status)

    def pleaseWait(self, message):
        """
        Display a please wait message, enabling metarefresh.
        """

        self.session().setValue("grid_job_wait", message)
        self.session().setValue("grid_job_metarefresh", "")
        self.writeHead()
        self.writeBody()
        self.response().flush()
               
    def queryGrid(self):
        """
        Query grid for job status
        """
        
        self.arcClient.updateStatus()
        self.writeBody()
        
    def showOutputWindow(self, jobId, jobName, outputType="stdout"):
        """
        Open output window.
        """
        
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
        
    def actions(self):
        """
        Return a list of implemented actions.
        """
        return ApplicationSecurePage.actions(self) + ["getJob",
             "killJob",
             "cleanJob",
             "queryGrid"]

