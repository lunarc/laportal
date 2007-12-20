
"""WelcomePage module"""

import os, string, pickle

from Web.JsonPage import JsonPage
from HyperText.HTML import *

import Lap
import Lap.Session

import LapSite

import simplejson

class JsonJobList(JsonPage):
	"""Empty page displaying the default welcome text."""
	
	def __findJobDefs(self):
		
		if self.session().hasValue("authenticated_user"):
	
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
							
			return jobs
		else:
			return []
						
	def onRenderJson(self):
		
		jobDefList = self.__findJobDefs()
		
		jobDefTreeList = []
		
		i = 2000
		
		for jobDef in jobDefList:
			item = {}
			item["text"] = jobDef[0] + " - " + jobDef[1]
			item["id"] = i
			item["leaf"] = True
			item["cls"] = "file"
			# https://malina.byggmek.lth.se/lap/context/Plugins/Abaqus/CustomJobPage?editjob=test
			item["url"] = self.pageLoc()+jobDef[2]+"?editjob=%s" % jobDef[0]
			jobDefTreeList.append(item)
			i+=1
		
		jsonString = simplejson.dumps(jobDefTreeList)
		self.writeln(jsonString)
	

							
