import os, sys, string

import Lap.Job

abaqusShellTemplate = """#!/bin/sh
abaqus job=%(jobIdentifier)s user=%(userRoutine)s interactive
"""

abaqusEnvFileTemplate = """abaquslm_license_file="27000@%(licenseServer)s" 
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("ABAQUS (user)")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
		attribs["inputFile"] = "sample.inp"
		attribs["userRoutine"] = ""
		attribs["licenseServer"] = ""

		# XRSL specific attributes		

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/FEA/ABAQUS-6.6"

		self.addInputFile("run.sh")
		self.addInputFile("abaqus_v6.env")

		self.addOutputFile("/")
		
	def setInputFile(self, filename):
	
		self.getAttributes()["inputFile"] = filename
		
	def setUserRoutine(self, filename):
		
		self.getAttributes()["userRoutine"] = filename
		
	def refresh(self):
		
		# XRSL attributes, not changing over time

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/FEA/ABAQUS-6.6"
		
	def setup(self):

		# Get directory and attributes	
		
		taskDir = self.getDir()
		attribs = self.getAttributes()

		self.addInputFile(attribs["inputFile"])
		self.addInputFile(attribs["userRoutine"])
		
		# Create abaqus env file 
		
		envFile = file(os.path.join(taskDir,"abaqus_v6.env"), "w")
		envFile.write(abaqusEnvFileTemplate % {"licenseServer":attribs["licenseServer"]})
		envFile.close()

		# Create shell script
		
		jobIdentifier, ext = os.path.splitext(attribs["inputFile"])
		
		shellFile = file(taskDir+"/run.sh", "w")
		shellFile.write(abaqusShellTemplate %  {"jobIdentifier":jobIdentifier, "userRoutine":attribs["userRoutine"]})
		shellFile.close()

		# Create XRSL file

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
