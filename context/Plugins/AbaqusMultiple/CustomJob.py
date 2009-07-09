import os, sys, string

import Lap.Job

abaqusShellTemplate = """#!/bin/sh
abaqus job=%(jobIdentifier)s interactive
"""

abaqusEnvFileTemplate = """abaquslm_license_file="27000@%(licenseServer)s" 
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("ABAQUS Multiple")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
		attribs["inputFiles"] = []
		attribs["licenseServer"] = ""
		attribs["multipleJobs"] = False

		self.addOutputFile("/")
		
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

		# Create abaqus env file 
		
		envFile = file(os.path.join(taskDir,"abaqus_v6.env"), "w")
		envFile.write(abaqusEnvFileTemplate % {"licenseServer":attribs["licenseServer"]})
		envFile.close()
		
		if self.isMultipleJob():
			
			# Create shell scripts, multiple job multiple processors
			
			# Copy the xrsl attributes, so that we can modify them
			# for each job
			
			xrslWriter = Lap.Job.XRSLWriter()
			xrslWriter.setFilename(taskDir+"/job.xrsl")
		
			for inputFile in attribs["inputFiles"]:

				jobIdentifier, ext = os.path.splitext(inputFile)
				shellFile = file(taskDir+"/run_%s.sh" % jobIdentifier, "w")
				shellFile.write("#!/bin/sh\n")
				shellFile.write("abaqus job=%s interactive\n" % jobIdentifier)
				shellFile.close()
				
				# Create XRSL file
				
				xrslAttribs = self.getXRSLAttributes().copy()
				
				xrslAttribs["inputFiles"] = {}
				xrslAttribs["inputFiles"]["run_%s.sh" % jobIdentifier] = ""
				xrslAttribs["inputFiles"]["abaqus_v6.env"] = ""
					
				baseJobName = xrslAttribs["jobName"]
					
				xrslAttribs["inputFiles"][inputFile] = ""
				xrslAttribs["arguments"] = "./run_%s.sh" % jobIdentifier
				xrslAttribs["jobName"] = "%s_%s_multiple" % (baseJobName, jobIdentifier)
				
				xrslWriter.addXRSLAttributes(xrslAttribs)
					
			xrslWriter.write()
					
					
		else:

			# Create shell script, multiple job single processor
			
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write("#!/bin/sh\n")
			
			for inputFile in attribs["inputFiles"]:
				jobIdentifier, ext = os.path.splitext(inputFile)
				shellFile.write("mkdir %s\n" % jobIdentifier)
				shellFile.write("mv %s %s\n" % (inputFile, jobIdentifier))
				shellFile.write("pushd %s\n" % (jobIdentifier))
				shellFile.write("abaqus job=%s interactive\n" % jobIdentifier)
				shellFile.write("popd\n")
			
			shellFile.close()
	
			# Create XRSL file
				
			xrslAttribs = self.getXRSLAttributes()
			xrslAttribs["inputFiles"] = {}

			for inputFile in attribs["inputFiles"]:
				xrslAttribs["inputFiles"][inputFile] = ""
			
			xrslAttribs["inputFiles"]["run.sh"] = ""
			xrslAttribs["inputFiles"]["abaqus_v6.env"] = ""
	
			xrslFile = Lap.Job.XRSLFile(self)
			xrslFile.setFilename(taskDir+"/job.xrsl")
			xrslFile.write()
		

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
				
	def addInputFile(self, inputFile):
		self.getAttributes()["inputFiles"].append(inputFile)
		
	def removeInputFile(self, inputFile):
		self.getAttributes()["inputFiles"].remove(inputFile)
		
	def clearInputFiles(self):
		self.getAttributes()["inputFiles"] = []

	def setMultipleJob(self, flag):
		self.getAttributes()["multipleJobs"] = flag
		
	def isMultipleJob(self):
		if not self.getAttributes().has_key("multipleJobs"):
			self.getAttributes()["multipleJobs"] = False
			
		return self.getAttributes()["multipleJobs"]
