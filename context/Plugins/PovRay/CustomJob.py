import os, sys, string

from zipfile import ZipFile

import Lap.Job

povRayIniTemplate = """Display=off
Initial_Frame=%(initialFrame)s
Final_Frame=%(finalFrame)s
Input_File_Name=%(povFile)s
Cyclic_Animation=On
Pause_when_Done=Off
Output_File_Type=N
+W%(imageWidth)s +H%(imageHeight)s;

Antialias=%(antialias)s
+am2
Antialias_Threshold=%(antialiasThreshold)s
Antialias_Depth=%(antialiasDepth)s
Test_Abort_Count=100
"""

povRayShellTemplate = """#!/bin/sh
mkdir images
cp *.ini images
cp *.pov images
cd images
povray %(iniFile)s
cd ..
tar czf images.tar.gz images
"""

povRayZipShellTemplate = """#!/bin/sh
mkdir images
mv %(zipFilename)s images
mv *.ini images
cd images
unzip %(zipFilename)s
povray %(iniFile)s
cd ..
tar czf images.tar.gz images
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("POVRay")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		self.povFile = ""

		attribs = self.getAttributes()
		attribs["initialFrame"] = 0
		attribs["finalFrame"] = 1
		attribs["imageWidth"] = 1024
		attribs["imageHeight"] = 768
		attribs["povFile"] = ""
		attribs["iniFile"] = "settings.ini"
		attribs["antialias"] = True
		attribs["antialiasThreshold"] = 0.25
		attribs["antialiasDepth"] = 1.0
		
	def refresh(self):

		# XRSL specific attributes		

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "POVRAY"
		
		# Update new attributes
		
		attribs = self.getAttributes()
		
		if not attribs.has_key("antialias"):
			attribs["antialias"] = True
			
		if not attribs.has_key("antialiasThreshold"):
			attribs["antialiasThreshold"] = 0.25
		
		if not attribs.has_key("antialiasDepth"):
			attribs["antialiasDepth"] = 1.0
		
	def setPovrayFile(self, filename):
	
		print "Settings povrayfile."
		self.getAttributes()["povFile"] = filename
		
	def setup(self):

		# Get directory and attributes
		
		self.clearInputFiles()
		self.clearOutputFiles()
		
		taskDir = self.getDir()
		attribs = self.getAttributes()

		self.addInputFile("run.sh")
		self.addInputFile("settings.ini")

		self.addOutputFile("images")
		self.addOutputFile("images.tar.gz")
		
		# Check if file is a zip/gz-archive
		
		path, ext = os.path.splitext(attribs["povFile"])
		
		povFilename = attribs["povFile"]
		zipFilename = ""
		uncompressZip = False
		uncompressTar = False
		
		if ext == ".zip":
			zipfile = ZipFile(taskDir+"/"+attribs["povFile"])
			nameList = zipfile.namelist()
			zipfile.close()
			
			zipFilename = attribs["povFile"]
			
			uncompressZip = True
			
			for name in nameList:
				path, ext = os.path.splitext(name)
				if ext == ".pov":
					povFilename = name

		self.addInputFile(attribs["povFile"])

		# Create a povray ini file
		
		if attribs["antialias"]:
			antialiasFlag = "On"
		else:
			antialiasFlag = "Off"

		iniFile = file(taskDir+"/settings.ini" , "w")
		iniFile.write(povRayIniTemplate %
					  {"initialFrame":str(attribs["initialFrame"]),
					   "finalFrame":str(attribs["finalFrame"]),
					   "imageWidth":str(attribs["imageWidth"]),
					   "imageHeight":str(attribs["imageHeight"]),
					   "povFile":povFilename,
					   "antialias":antialiasFlag,
					   "antialiasDepth":str(attribs["antialiasDepth"]),
					   "antialiasThreshold":str(attribs["antialiasThreshold"])})
		iniFile.close()

		# Create shell script
		
		if uncompressZip:
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write(povRayZipShellTemplate % {"iniFile":"settings.ini", "zipFilename":zipFilename})
			shellFile.close()
		else:
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write(povRayShellTemplate % {"iniFile":"settings.ini"})
			shellFile.close()
			

		# Create XRSL file

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
