#
# LAP Numpy Single Plugin - Version 0.8
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

import os, sys, string

import Lap.Job

import arc
from Grid.Clients import *

runScriptTemplate = """#!/bin/sh
python %s
"""

class CustomTask(Lap.Job.LapBaseTask):
    def __init__(self):
        Lap.Job.LapBaseTask.__init__(self)
        
        self.description = "NumPy"
        self.taskEditPage = "CustomJobPage"

        # Task specific attributes
        
        self.__mainFile = ""      
        self.packages = []
        self.extraFiles = []
        
    def doCreateRunScript(self, taskName, taskId):
        """
        Abstract routine responsible for returning a
        run-script for the job.
        """
        return runScriptTemplate % (self.__mainFile)
        
    def doCreateJobDescription(self, taskName, taskId, taskDir):
        """
        Abstract routines responsible for returning a jobdescription for
        the job.
        """
        
        # Create a managed job description
        
        job = ManagedJobDescription();
        job.JobName = str(taskName)
        job.TotalWallTime = arc.Period(str(self.cpuTime),arc.PeriodMinutes)
        job.Executable = "/bin/sh"
        job.addArgument("run.sh")
        
        # Make sure we store the full paths of input files
        
        for inputFile in self.inputFiles.keys():
            url = self.inputFiles[inputFile]
            if url == "":
                fullPath = os.path.join(taskDir, inputFile)
                job.addInputFile(fullPath)
            else:
                job.addInputFile(inputFile, url)
        
        #job.addRuntimeEnvironment("ENV/PYTHON","2.4.3")
        job.Output = "stdout.txt"
        job.Error = "stderr.txt"
        
        return job    
            
    def setMainFile(self, filename):
        self.__mainFile = filename
        self.addInputFile(self.__mainFile)
        
    def getMainFile(self):
        return self.__mainFile
        
    def addPackage(self, filename):
        pass
    
    def addExtraFile(self, filename):
        pass
    
    def removePackage(self, filename):
        pass
    
    def removeExtraFile(self, filename):
        pass
            
    mainFile = property(getMainFile, setMainFile)


