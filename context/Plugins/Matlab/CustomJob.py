#
# LAP Matlab Single Plugin - Version 0.8
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

		self.setDescription("MATLAB")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		attribs = self.getAttributes()
		attribs["mainFile"] = ""
		attribs["packages"] = []
		attribs["extra"] = []

		self.addOutputFile("/")
		
	def refresh(self):

		# XRSL attributes, not changing over time
		
		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "APPS/MATH/MATLAB"
		
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
		
	def addExtraFile(self, extraFilename):
		self.getAttributes()["extra"].append(extraFilename)
		
	def removeExtraFile(self, extraFilename):
		packages = self.getAttributes()["extra"]
		packages.remove(extraFilename)
		
	def clearExtraFiles(self):
		attribs = self.getAttributes()
		attribs["extra"] = []

	def setup(self):

		# Get directory and attributes	
		

		taskDir = self.getDir()
		attribs = self.getAttributes()

		mainFile = attribs["mainFile"]
		extraFiles = attribs["extra"]
		
		# Define input files
		
		self.clearInputFiles()		
		self.addInputFile("run.sh")
		
		if mainFile!="":
			self.addInputFile(mainFile)
		
		for extraFile in extraFiles:
			self.addInputFile(extraFile)
		
		# Create shell script
		
		matlabPathList = []
		
		shellFile = file(taskDir+"/run.sh", "w")
		shellFile.write("#!/bin/sh\n")

		print self.getXRSLAttributes().copy()
		
		for packageFilename in attribs["packages"]:
			shellFile.write("unzip %s > /dev/null\n" % packageFilename)
			print "packageFilename = ", packageFilename
			packageDir, ext = os.path.splitext(packageFilename)
			print "packageDir = ", packageDir
			matlabPathList.append("'./%s'" % packageDir)
			self.addInputFile(packageFilename)
		
		shellFile.write("matlab -nodisplay -nosplash -nojvm < matlab_wrapper.m \n" )
		shellFile.write("rm -f ./*.zip > /dev/null\n")
		
		for packageFilename in attribs["packages"]:
			packageDir, ext = os.path.splitext(packageFilename)
			shellFile.write("rm -rf ./%s > /dev/null\n" % packageDir)			
		
		shellFile.close()
		
		# Create MATLAB wrapper script (adds path and exit at end)
		
		mainScript = mainFile.split(".")[0]
		
		wrapperFile = file(taskDir+"/matlab_wrapper.m", "w")
		
		for matlabPath in matlabPathList:
			wrapperFile.write("path(path, %s);\n" % matlabPath)
			
		wrapperFile.write(mainScript + "\n")
		wrapperFile.write("exit\n")
		wrapperFile.close()
		
		self.addInputFile("matlab_wrapper.m")		

		# Create XRSL file
		
		print self.getXRSLAttributes().copy()

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
