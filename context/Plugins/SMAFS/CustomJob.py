import os, sys, string

import Lap.Job

smafsShellTemplate = """#!/bin/sh
cat $PARNODES > %(jobIdentifier)s_nodfile
echo "add " `cat $PARNODES` | pvm
echo "conf" | pvm
smafs t %(jobIdentifier)s p %(count)d c
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("SMAFS")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
		attribs["inputFile"] = ""
		
		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["count"] = 4

		self.addOutputFile("/")
		
	def refresh(self):
		
		# XRSL attributes, not changing over time

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/CFD/SMAFS"
		
	def setInputFile(self, filename):
	
		self.getAttributes()["inputFile"] = filename
		
	def setup(self):

		# Get directory and attributes	
		
		taskDir = self.getDir()
		attribs = self.getAttributes()
		xrslAttribs = self.getXRSLAttributes();
		
		# Define input files
		
		self.clearInputFiles()

		self.addInputFile("run.sh")
		self.addInputFile(attribs["inputFile"])
		
		# Create shell script
		
		jobIdentifier, ext = os.path.splitext(attribs["inputFile"])
		
		shellFile = file(taskDir+"/run.sh", "w")
		shellFile.write(smafsShellTemplate %  {"jobIdentifier":jobIdentifier, "count":xrslAttribs["count"]})
		shellFile.close()

		# Create XRSL file

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
