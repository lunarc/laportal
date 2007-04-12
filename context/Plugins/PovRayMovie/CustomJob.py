import os, sys, string

from zipfile import ZipFile

import Lap.Job

povRayIniTemplate = """
Antialias=On

Display=off

Antialias_Threshold=0.1
Antialias_Depth=2
Input_File_Name=%(povFilename)s

Width=640
Height=480

Initial_Frame=%(startFrame)d
Final_Frame=%(endFrame)d

Subset_Start_Frame=%(subsetStartFrame)d
Subset_End_Frame=%(subsetEndFrame)d

Initial_Clock=0
Final_Clock=1

Cyclic_Animation=on
Pause_when_Done=off
"""

povRayPythonCode = r"""#!/bin/env python

import os
import sys
import commands

def jobInfo():
        result = commands.getstatusoutput('hostname')
        hostname = result[1]
        nodes = os.environ["PARNODES"]
        nodes = nodes.split("\n")
        return [nodes.index(hostname)+1, len(nodes)]

# Determine current node and number of nodes

def renderPovRay(povRaySource, initialFrame, finalFrame):

        currentNode, numberOfNodes = jobInfo()

        rootName, ext = os.path.splitext(povRaySource)

        povRayIniName = "%s_%d.ini" % (rootName, currentNode)
        framesPerNode = int(finalFrame / numberOfNodes)
        remainingFrames = finalFrame - framesPerNode*numberOfNodes - 1
        startFrame = initialFrame
        nodeRanges = []

        nodeRanges = []

        i = 1

        while i<=numberOfNodes:
                if currentNode!=numberOfNodes:
                        nodeRanges.append([startFrame,startFrame+framesPerNode-1])
                else:
                        nodeRanges.append([startFrame,startFrame+framesPerNode+remainingFrames])
                i = i + 1
                startFrame = startFrame + framesPerNode

        nodeRange = nodeRanges[currentNode-1]

        # Create ini-file
	
	iniFileTemplate = file("./template.ini", "r")
	iniTemplate = iniFileTemplate.read()
	iniFileTemplate.close()

        iniFile = open(povRayIniName,'w')

        iniTemplateTuple = {'povFilename':povRaySource,
                'startFrame':initialFrame,
                'endFrame':finalFrame,
                'subsetStartFrame':nodeRange[0],
                'subsetEndFrame':nodeRange[1]}

        iniFile.write(iniTemplate % iniTemplateTuple)
        iniFile.close()

        # Start rendering

        retVal, outputLines = commands.getstatusoutput("povray %s" % (povRayIniName))

        return retVal

if __name__ == "__main__":

        if len(sys.argv)!=4:
                print "Too few arguments"
                print sys.argv
                sys.exit(-1)

        povRaySource = sys.argv[1]
        initialFrame = int(sys.argv[2])
        finalFrame = int(sys.argv[3])

        renderPovRay(povRaySource, initialFrame, finalFrame)	
"""

povRayShellTemplate = """#!/bin/sh

# Input parameters

POVRAY_FILENAME=%(povFilename)s
MPEG_FILENAME=%(mpegFilename)s

START_FRAME=%(startFrame)d
END_FRAME=%(endFrame)d

# Configuration parameters

OUTPUT_DIR=`pwd`

# Copy files

echo Copy files to nodes...
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.pov $SCRATCH
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.py $SCRATCH
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.ini $SCRATCH

# Run PovRay

echo Run parallel PovRay...
cd $SCRATCH
$PARRUN $PARARGS ./run.py $POVRAY_FILENAME $START_FRAME $END_FRAME
cd $OUTPUT_DIR

# Copy back files

echo Copying files back from local disk...
$PARRUN $PARARGS cp $SCRATCH/\*.png $OUTPUT_DIR

# Executing mpeg generation on master node

echo Creating mpeg movie...
convert -verbose -quality 90 *.png $MPEG_FILENAME
"""

povRayZipShellTemplate = """#!/bin/sh

# Input parameters

ZIP_FILENAME=%(zipFilename)s
POVRAY_FILENAME=%(povFilename)s
MPEG_FILENAME=%(mpegFilename)s

START_FRAME=%(startFrame)d
END_FRAME=%(endFrame)d

# Configuration parameters

OUTPUT_DIR=`pwd`

# Decompress archive

unzip %(ZIP_FILENAME)s

# Copy files

echo Copy files to nodes...
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.pov $SCRATCH
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.py $SCRATCH
$PARRUN $PARARGS cp $OUTPUT_DIR/\*.ini $SCRATCH

# Run PovRay

echo Run parallel PovRay...
cd $SCRATCH
$PARRUN $PARARGS ./run.py $POVRAY_FILENAME $START_FRAME $END_FRAME
cd $OUTPUT_DIR

# Copy back files

echo Copying files back from local disk...
$PARRUN $PARARGS cp $SCRATCH/\*.png $OUTPUT_DIR

# Executing mpeg generation on master node

echo Creating mpeg movie...
convert -verbose -quality 90 *.png $MPEG_FILENAME
"""

class CustomTask(Lap.Job.Task):
	def __init__(self):
		Lap.Job.Task.__init__(self)

		self.setDescription("POVRayMovie")
		self.setTaskEditPage("CustomJobPage")

		# Task specific attributes

		self.povFilename = ""

		attribs = self.getAttributes()
		attribs["startFrame"] = 0
		attribs["endFrame"] = 1
		attribs["imageWidth"] = 1024
		attribs["imageHeight"] = 768
		attribs["povFilename"] = ""
		attribs["iniFilename"] = "settings.ini"
		attribs["antialias"] = True
		attribs["antialiasThreshold"] = 0.25
		attribs["antialiasDepth"] = 1.0
		
		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["count"] = 2
		
	def refresh(self):

		# XRSL specific attributes		

		xrslAttribs = self.getXRSLAttributes()
		xrslAttribs["executable"] = "/bin/sh"
		xrslAttribs["arguments"] = "./run.sh"
		xrslAttribs["runTimeEnvironment"] = "POVRAYMPEG"
		
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
		self.getAttributes()["povFilename"] = filename
		
	def setup(self):

		# Get directory and attributes
		
		self.clearInputFiles()
		self.clearOutputFiles()
		self.clearExecutableTags()
		
		taskDir = self.getDir()
		attribs = self.getAttributes()

		self.addInputFile("run.sh")
		self.addInputFile("template.ini")
		self.addInputFile("run.py")
		
		self.tagAsExecutable("run.sh")
		self.tagAsExecutable("run.py")

		# Check if file is a zip/gz-archive
		
		path, ext = os.path.splitext(attribs["povFilename"])
		
		povFilename = attribs["povFilename"]
		mpegFilename = path + ".mpg"
		zipFilename = ""
		uncompressZip = False
		uncompressTar = False
		
		self.addOutputFile(mpegFilename)
		
		if ext == ".zip":
			zipfile = ZipFile(taskDir+"/"+attribs["povFilename"])
			nameList = zipfile.namelist()
			zipfile.close()
			
			zipFilename = attribs["povFilename"]
			
			uncompressZip = True
			
			for name in nameList:
				path, ext = os.path.splitext(name)
				if ext == ".pov":
					povFilename = name

		self.addInputFile(attribs["povFilename"])

		# Create a povray ini file
		
		iniFile = file(taskDir+"/template.ini" , "w")
		iniFile.write(povRayIniTemplate)
		iniFile.close()
		
		# Create python script
		
		pyFile = file(taskDir+"/run.py", "w")
		pyFile.write(povRayPythonCode)
		pyFile.close()

		# Create shell script
		
		if uncompressZip:
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write(povRayShellTemplate %
					{"iniFilename":"settings.ini",
					 "startFrame":attribs["startFrame"],
					 "endFrame":attribs["startFrame"],
					 "mpegFilename":mpegFilename,
					 "povFilename":povFilename,
					 "zipFilename":zipFilename})
			shellFile.close()
		else:
			shellFile = file(taskDir+"/run.sh", "w")
			shellFile.write(povRayShellTemplate %
					{"iniFilename":"settings.ini",
					 "startFrame":attribs["startFrame"],
					 "endFrame":attribs["endFrame"],
					 "mpegFilename":mpegFilename,
					 "povFilename":povFilename})
			shellFile.close()
			

		# Create XRSL file
		
		print self.getXRSLAttributes()

		xrslFile = Lap.Job.XRSLFile(self)
		xrslFile.setFilename(taskDir+"/job.xrsl")
		xrslFile.write()

	def clean(self):
		if self.getDir()!="":
			for filename in os.listdir(self.getDir()):
				os.remove(os.path.join(self.getDir(), filename))
