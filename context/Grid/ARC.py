#
# ARC middleware interface module
#
# Copyright (C) 2006-2007 Jonas Lindemann
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

"""ARC middleware interface module."""

import os, sys, string, commands, threading

import Security
import Web.Utils
import Lap.System

import LapSite

import arclib

from Lap.Log import *

class Ui:
	"""ARC middleware user interface class."""
	_sharedState = {}
	def __init__(self, user):
		"""Class constructor"""
		self.__dict__ = self._sharedState
		
		self._arclibLock = threading.Lock()

		self._user = user
		self._proxy = Security.Proxy(self._user.getProxy())
		self._debugLevel = 1
		
		self._env = {}
		
		self._env["X509_USER_PROXY"] = self._proxy.getFilename()
		self._env["HOME"] = self._user.getDir()

	def lockArclib(self):
		self._arclibLock.acquire()
		self.setupEnviron()

	def unlockArclib(self):
		self._arclibLock.release()

	def setupEnviron(self):
		os.environ["X509_USER_PROXY"]=self._proxy.getFilename()
		os.environ["HOME"] = self._user.getDir()
				
	def setDebugLevel(self, debugLevel):
		"""Set the desired debug output level fo the ARC commands.
		
		@type  debugLevel: int
		@param debugLevel: from -3 (quiet) to 3 (verbose) - default 0 (int)"""
		self._debugLevel = debugLevel
		
	def getDebugLevel(self):
		"""Return debug output level from the ARC commands.
		
		@rtype: int"""
		return self._debugLevel
				
	def sync(self):
		"""Query grid for jobs and update job list.
		
		@rtype: list
		@return: list of [resultVal, result], where resultVal is the return value
		from the ARC command and result is a list of command output."""
		resultVal, result = Lap.System.getstatusoutput("ngsync -f -d %d" % self._debugLevel, self._env)		
		
	def get(self, jobID, downloadDir = "", dirTag = ""):
		"""Download results from grid job.
		
		@type  jobId: string
		@param jobID: jobId URL identifier.
		@type  downloadDir: string
		@param downloadDir: Download results to specified directory.
		@type  dirTag: string
		@param dirTag: Add a special tag after the download directory (guid_[dirTag])."""
		if downloadDir=="":
			resultVal, result = Lap.System.getstatusoutput("ngget %s" % jobID, self._env)
		else:
			if dirTag=="":
				resultVal, result = Lap.System.getstatusoutput("ngget -dir %s %s" % (downloadDir, jobID), self._env)
			else:
				resultVal, result = Lap.System.getstatusoutput("ngget -dir %s %s" % (downloadDir, jobID), self._env)
				jobIDParts = jobID.split("/")
				jobUID = jobIDParts[len(jobIDParts)-1]
				os.rename("%s/%s" % (downloadDir, jobUID), "%s/%s_%s" % (downloadDir, jobUID, dirTag))
				
		return resultVal
	
	def clean(self, jobID):
		"""Removes a job from a remote cluster.
		
		@type  jobID: string
		@param jobID: jobId URL identifier."""

		if LapSite.System["ARCInterface"] == "arclib":
			self.lockArclib()
			try:
				arclib.CleanJob(jobID)
			except arclib.FTPControlError:
				arclib.RemoveJobID(jobID)
			self.unlockArclib()
		else:
			resultVal, result = Lap.System.getstatusoutput("ngclean %s" % jobID, self._env)		
		
		return resultVal
	
	def copy(self, source, dest):
		"""Copy file from source URL to dest URL.
		
		@type  source: string
		@param source: URL of file to copy from.
		@type  dest: string
		@param dest: URL destination file."""
		resultVal, result = Lap.System.getstatusoutput("ngcp %s %s" % (source, dest), self._env)		
		
		return resultVal

	def pcopy(self, source):
		"""Open the ngcp command as a popen process, redirecting output
		to stdout and return process file handle.
		
		@type  source: string
		@param source: URL to open"""
		f = Lap.System.popen("ngcp %s /dev/stdout" % source, self._env)		
		
		return f

	def kill(self, jobID):
		"""Kill a running job.
		
		@type  jobID: string
		@param jobID: jobId URL identifier."""		
		resultVal, result = Lap.System.getstatusoutput("ngkill %s" % jobID, self._env)		
		
		return resultVal
	
	def jobStatus(self):
		"""Query status of jobs in joblist.
		
		The command returns a dictionary of jobIDs. Each item
		in the dictionary consists of an additional dictionary with the
		attributes:
		
			name = Job name
			status = ARC job states, ACCPTED, SUBMIT, INLRMS etc
			error = Error status
			
		If there was an error None is returned.
			
		Example:
		
			jobList = ui.jobStatus()
		
			print jobList['gsiftp://...3217']['name']
			print jobList['gsiftp://...3217']['status']
			
			
		@rtype: dict
		@return: job status dictionary."""
		
		if LapSite.System["ARCInterface"] == "arclib":

			jobList = {}

			self.lockArclib()
			try:	
				jobIds = arclib.GetJobIDs()
			except:
				self.unlockArclib()

			print jobIds

			self.unlockArclib()
			
			jobListFile = file(os.path.join(self._user.getDir(),".ngjobs"), "r")
			lines = jobListFile.readlines()
			jobListFile.close()
			
			for line in lines:
				jobId, jobName = line.strip().split("#")
				print "Querying job =", jobId, jobName
				jobList[jobId] = {}
				jobList[jobId]["name"] = jobName

				status = 0
				exitCode = 0
				
				self.lockArclib()

				try:
					jobInfo = arclib.GetJobInfoDirect(jobId)
					status = jobInfo.status
					exitCode = jobInfo.exitcode
				except arclib.FTPControlError:
					print "Failed to query job = ", jobName
					status = "REMOVED"
					exitCode = -1

				self.unlockArclib()
				
				jobList[jobId]["status"] = status
				jobList[jobId]["error"] = exitCode
			
			if len(lines)==0:
				return []
			else:
				return jobList

		else:

			resultVal, result = Lap.System.getstatusoutput("ngstat -a", self._env)		
	
			jobList = {}
			job = None
	
			try:
				for line in result:
					splitResult = string.split(line,":")
					if len(splitResult)>0:
						property = string.strip(splitResult[0])
		
						if property=="Job gsiftp":
							if job!=None:
								jobList[jobID] = job
								
							job = {}
							splitResult2 = string.strip(line," ")
							jobID = line[4:]
		
						if property=="Jobname":
							job["name"] = string.strip(line)[9:]
	
						if property=="Job Name":
							job["name"] = string.strip(line)[10:]
		
						if property=="Status":
							job["status"] = string.strip(line)[8:]
		
						if property=="Error":
							job["error"] = string.strip(line)[7:]
		
					if job!=None:
						jobList[jobID] = job
						
			except:
				return None
										
			return jobList
		
	def submit(self, xrslFilename, jobName=""):
		"""Submit xrsl file as job to available ARC resources.
		
		@type  xrslFilename: string
		@param xrslFilename: Filename containing a job description in XRSL.
		@rtype list:
		@return: list containing [resultVal, jobIds] resultVal is the return
		code of the ARC command, jobIds is a list of jobID strings."""
		
		if LapSite.System["ARCInterface"] == "arclib":
			
			currDir = ""
	
			try:
			
				# Convert XRSL file into a string
						
				f = file(xrslFilename, "r")
				xrslString = f.read()
				f.close()
				xrslAll = arclib.Xrsl(xrslString)
				
				# Check for multiple xrsl file
				
				xrslSplit = xrslAll.SplitMulti()
				
				# Find a cluster
			
				lapInfo("Ui: Getting cluster info...")
				url = arclib.URL("ldap://neo.lunarc.lu.se:2135/o=grid/mds-vo-name=local")
				cluster = arclib.GetClusterInfo(url)
				lapDebug(cluster)
				
				# Find queue information
		
				lapInfo("Ui: Getting queue info...")
				queueInfo = arclib.GetQueueInfo(url)
				lapDebug(queueInfo)
				
				# Construct submission targets
			
				lapInfo("Ui: Constructing targets...")
				targets = arclib.ConstructTargets(queueInfo, xrslAll)
				lapDebug(targets)
			
				# Submit job
				
				jobIds = []
				
				lapInfo("Ui: Submitting job...")
				if len(targets)>0:
					currDir = os.getcwd()
					[jobDir, filename] = os.path.split(xrslFilename)
					self._arclibLock.acquire()
					self.lockArclib()
					os.chdir(jobDir, force=True)
					for xrsl in xrslSplit:
						jobId = arclib.SubmitJob(xrsl, targets)
						jobIds.append(jobId)
						lapInfo("Ui:"+jobId+"submitted.")
						
						jobName = xrsl.GetRelation("jobName").GetSingleValue()
						
						arclib.AddJobID(jobId, jobName)
					os.chdir(currDir, force=True)
					self.unlockArclib()
					return 0, jobIds
				else:
					return -1, jobIds
					
				
			except arclib.XrslError, message:
				lapError("Ui: XrslError: "+message)
				os.chdir(currDir, force=True)
				self.unlockArclib()
				return -1, []
			except arclib.JobSubmissionError, message:
				lapError("Ui: JobSubmissionError: "+(message))
				os.chdir(currDir, force=True)
				self.unlockArclib()
				return -1, []			
			except arclib.TargetError, message:
                                lapError("Ui: TargetError: "+str(message))
                                os.chdir(currDir, force=True)
                                self.unlockArclib()
                                return -1, []
			except:
				lapError("Unexpected error: "+str(sys.exc_info()[0]))
				os.chdir(currDir, force=True)
				self.unlockArclib()
				return -1, []

		else:
		
			if not os.path.isfile(xrslFilename):
				return False
			
			[jobDir, filename] = os.path.split(xrslFilename)
			
			#oldDir = os.getcwd()
			#os.chdir(jobDir, force=True)
			
			commandLine = "ngsub -d %d -t %d -f %s" % (self._debugLevel, self._user.getSubmitTimeout(), xrslFilename)
			
			if len(self._user.getPreferredClusters())>0:
				for cluster in self._user.getPreferredClusters():
					commandLine = commandLine + " -c " + cluster
					
			if len(self._user.getRejectedClusters())>0:
				for cluster in self._user.getRejectedClusters():
					commandLine = commandLine + " -c -" + cluster
					
			#if self._user.getPreferredCluster() != "":
			#	commandLine = commandLine + " -c " + self._user.getPreferredCluster()
			
			resultVal, result = Lap.System.getstatusoutput(commandLine, self._env, jobDir)
			
			#os.chdir(oldDir, force=True)
			
			jobIds = []
			errorMessage = ""
			
			for line in result:
				gsiPos = line.find("gsiftp://")
				if gsiPos>=0:
					jobIds.append(line[gsiPos:].strip())
					
			return [resultVal, jobIds]
	
	def ls(self, url):
		"""List files at a specific URL.
		
		@type  url: string
		@param url: URL location to list files.
		@rtype: list
		@return: list of return value of ARC command and a dirListing. If
		the listing failed the second output parameter contains the error
		message."""
		commandLine = "ngls -l %s" % url
		
		resultVal, result = Lap.System.getstatusoutput(commandLine, self._env)
		
		dirListing = []
		
		if resultVal == 0:
			for line in result:
				if line!="":
					date = line.split('"')[1]
					filePart = line.split('"')[0]
					fileInfo = filePart.split(" ")
					dirEntry = [fileInfo[0], fileInfo[1], fileInfo[2], date]
					dirListing.append(dirEntry)
			return resultVal, dirListing
		else:
			return resultVal, result
		
		return resultVal, result
	
	def getStandardOutput(self, jobId):
		"""Get the standard output of a running job.
		
		@type  jobID: string
		@param jobID: jobId URL identifier.
		@rtype: list
		@return: list of return value from ARC and output from job."""
		resultVal, result = Lap.System.getstatusoutput("ngcat -o %s" % jobId, self._env)		
		
		return resultVal, result
		
	def getStandardError(self, jobId):
		"""Get the standard error of a running job.
		
		@type  jobID: string
		@param jobID: jobId URL identifier.
		@rtype: list
		@return: list of return value from ARC and output from job."""
		resultVal, result = Lap.System.getstatusoutput("ngcat -e %s" % jobId, self._env)		
		
		return resultVal, result
	
	def getGridLog(self, jobId):
		"""Get the grid log of a running job.
		
		@type  jobID: string
		@param jobID: jobId URL identifier.
		@rtype: list
		@return: list of return value from ARC and output from job."""
		resultVal, result = Lap.System.getstatusoutput("ngcat -l %s" % jobId, self._env)		
		
		return resultVal, result
		
		
