#
# LAP MATLAB Multiple Plugin - Version 0.8
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

import os, sys, string

import Lap.Job

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("MATLAB multiple")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
		attribs["mainFile"] = "main.m"
		attribs["packages"] = []
		attribs["mainFiles"] = []
		attribs["extra"] = []
		attribs["multipleJobs"] = False

		self.addOutputFile("/")
		
	def refresh(self):
		
		# XRSL attributes not changing 	

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/MATH/MATLAB"
		
	def addMainFile(self, mainFile):
		self.getAttributes()["mainFiles"].append(mainFile)
		
	def removeMainFile(self, mainFile):
		self.getAttributes()["mainFiles"].remove(mainFile)
		
	def clearMainFiles(self):
		self.getAttributes()["mainFiles"] = []
		
	def addExtraFile(self, mainFile):
		self.getAttributes()["extra"].append(mainFile)
		
	def removeExtraFile(self, mainFile):
		self.getAttributes()["extra"].remove(mainFile)
		
	def clearExtraFiles(self):
		self.getAttributes()["extra"] = []

	def setMultipleJob(self, flag):
		self.getAttributes()["multipleJobs"] = flag
		
	def isMultipleJob(self):
		if not self.getAttributes().has_key("multipleJobs"):
			self.getAttributes()["multipleJobs"] = False
			
		return self.getAttributes()["multipleJobs"]		
		
	def setMainFile(self, filename):
	
		self.getAttributes()["mainFile"] = filename
		
	def addPackage(self, packageFilename):
		attribs = self.getAttributes()
		attribs["packages"].append(packageFilename)
		
	def removePackage(self, packageFilename):
		packages = self.getAttributes()["packages"]
		packages.remove(packageFilename)
		
	def clearPackages(self):
		attribs = self.getAttributes()
		attribs["packages"] = []
		
	def setup(self):

		# Get directory and attributes	
		
		taskDir = self.getDir()
		attribs = self.getAttributes()
		
		if self.isMultipleJob():

			# Create shell scripts, multiple job multiple processors
			
			# Copy the xrsl attributes, so that we can modify them
			# for each job
			
			xrslWriter = Lap.Job.XRSLWriter()
			xrslWriter.setFilename(taskDir+"/job.xrsl")
		
			for mainFile in attribs["mainFiles"]:
				
				# Make a copy of the xrsl attributes
				
				xrslAttribs = self.getXRSLAttributes().copy()
				xrslAttribs["inputFiles"] = {}
				
				# Create run.sh for each main file
				
				jobIdentifier, ext = os.path.splitext(mainFile)

				shellFile = file(taskDir+"/run_%s.sh" % jobIdentifier, "w")
				shellFile.write("#!/bin/sh\n")
				
				matlabPathList = []
							
				# Add packaged and package handling code
				
				for packageFilename in attribs["packages"]:
					shellFile.write("unzip %s > /dev/null\n" % packageFilename)
					print "packageFilename = ", packageFilename
					packageDir, ext = os.path.splitext(packageFilename)
					print "packageDir = ", packageDir
					matlabPathList.append("'./%s'" % packageDir)
					xrslAttribs["inputFiles"][packageFilename] = ""
					
				# Create job execution code
				
				shellFile.write("matlab -nodisplay -nosplash -nojvm < matlab_wrapper_%s.m \n" % jobIdentifier )
				shellFile.write("rm -f ./*.zip > /dev/null\n")
				
				for packageFilename in attribs["packages"]:
					packageDir, ext = os.path.splitext(packageFilename)
					shellFile.write("rm -rf ./%s > /dev/null\n" % packageDir)			
				
				shellFile.close()
				
				# Create MATLAB wrappers for main files
							
				mainScript = mainFile.split(".")[0]
				
				wrapperFile = file(taskDir+"/matlab_wrapper_%s.m" % jobIdentifier, "w")
				
				for matlabPath in matlabPathList:
					wrapperFile.write("path(path, %s);\n" % matlabPath)
					
				wrapperFile.write(mainScript + "\n")
				wrapperFile.write("exit\n")
				wrapperFile.close()
				
				self.addInputFile("matlab_wrapper_%s.m" % jobIdentifier)		

				# Add files to xrsl

				xrslAttribs["inputFiles"]["run_%s.sh" % jobIdentifier] = ""
				xrslAttribs["inputFiles"][mainFile] = ""
				xrslAttribs["inputFiles"]["matlab_wrapper_%s.m" % jobIdentifier] = ""
				for packageFilename in attribs["packages"]:
					xrslAttribs["inputFiles"][packageFilename] = ""
					
				for extraFilename in attribs["extra"]:
					xrslAttribs["inputFiles"][extraFilename] = ""
					
				# Set job information
				
				baseJobName = xrslAttribs["jobName"]
					
				xrslAttribs["arguments"] = "./run_%s.sh" % jobIdentifier
				xrslAttribs["jobName"] = "%s_%s_multiple" % (baseJobName, jobIdentifier)
				
				xrslWriter.addXRSLAttributes(xrslAttribs)
					
			xrslWriter.write()
			
		else:

			# Create shell script
			
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write("#!/bin/sh\n")
	
			matlabPathList = []
			
			xrslAttributes = self.getXRSLAttributes()
			
			for packageFilename in attribs["packages"]:
				shellFile.write("unzip %s > /dev/null\n" % packageFilename)
				print "packageFilename = ", packageFilename
				packageDir, ext = os.path.splitext(packageFilename)
				print "packageDir = ", packageDir
				matlabPathList.append("'./%s'" % packageDir)
						
			for mainFile in attribs["mainFiles"]:
				jobIdentifier, ext = os.path.splitext(mainFile)				
				shellFile.write("matlab -nodisplay -nosplash -nojvm < matlab_wrapper_%s.m \n" % jobIdentifier )
				
			shellFile.write("rm -f ./*.zip > /dev/null\n")
			
			for packageFilename in attribs["packages"]:
				packageDir, ext = os.path.splitext(packageFilename)
				shellFile.write("rm -rf ./%s > /dev/null\n" % packageDir)			
			
			shellFile.close()
			
			# Create MATLAB wrapper files
			
			for mainFile in attribs["mainFiles"]:
			
				mainScript = mainFile.split(".")[0]
				
				wrapperFile = file(taskDir+"/matlab_wrapper_%s.m" % jobIdentifier, "w")
				
				for matlabPath in matlabPathList:
					wrapperFile.write("path(path, %s);\n" % matlabPath)
					
				wrapperFile.write(mainScript + "\n")
				wrapperFile.write("exit\n")
				wrapperFile.close()
				
				self.addInputFile("matlab_wrapper_%s.m" % jobIdentifier)		

			# Create XRSL file
			
			self.addInputFile("run.sh")
			
			for packageFilename in attribs["packages"]:
				self.addInputFile(packageFilename)
				
			for mainFile in attribs["mainFiles"]:
				self.addInputFile(mainFile)
				
			for extraFile in attribs["extra"]:
				self.addInputFile(extraFile)
			
			xrslFile = Lap.Job.XRSLFile(self)
			xrslFile.setFilename(taskDir+"/job.xrsl")
			xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
