#
# Job module
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

"""Job module"""

import string
import os
import sys

import Grid.ARC
import Lap.Utils

import shutil

class PropertyList:
    """Property list class.
    
    Implements a property list (Probarbly not needed...)"""
    def __init__(self):
        self.properties = {}

    def __len__(self):
        return len(self.properties)

    def __getitem__(self, key):
        return self.properties[key]

    def __setitem__(self, key, value):
        self.properties[key] = value

    def __delitem__(self, key):
        del self.properties[key]

    def __iter__(self):
        return self.properties

    def keys(self):
        return self.properties.keys()

    def items(self):
        return self.properties.items()
    
    def copy(self):
        return self.properties.copy()
    
    def has_key(self, key):
        return self.properties.has_key(key)

class XRSLAttributes(PropertyList):
    """XRSL Attribute class
    
    Defines the default XRSL attributes."""
    def __init__(self):
        PropertyList.__init__(self)
        self["executable"] = ""
        self["arguments"] = ""
        self["inputFiles"] = {}
        self["outputFiles"] = {}
        self["runTimeEnvironment"] = ""
        self["cpuTime"] = 60
        self["notify"] = ""
        self["memory"] = -1
        self["disk"] = -1
        self["stdin"] = ""
        self["stdout"] = "stdout.txt"
        self["stderr"] = "stderr.txt"
        self["jobName"] = "NoName"
        self["gmlog"] = "gmlog"
        self["cluster"] = ""
        self["startTime"] = ""
        self["rerun"] = -1
        self["architecture"] = ""
        self["count"] = -1
        self["executables"] = ""
        
class BaseTask(object):
    def __init__(self):
        self.name = "noname"
        self.description = ""
        self.executable = "/bin/sh"
        self.arguments = "run.sh"
        self.__inputFiles = {}
        self.__outputFiles = {}
        self.__runtimeEnvironments = []
        self.cpuTime = 60
        self.notify = ""
        self.memory = -1
        self.disk = -1
        self.stdin = ""
        self.stdout = "stdout.txt"
        self.stderr = "stderr.txt"
        self.logging = True
        self.__clusters = []
        self.architecture = ""
        self.__executables = []
        self.count = -1
        self.__version = "1.0"
        
        self.workDir="."
    
        self.sweepSize = 1
        self.__sweepParams = {"taskid":-1}
        
        self.calculateSweepValueFloat = None
        self.calculateSweepValueInt = None
        
        self.addInputFile("run.sh")
        
        self.doRefresh()
        
    def addInputFile(self, inputFile, url=""):
        self.__inputFiles[inputFile] = url
        
    def clearInputFiles(self):
        self.__inputFiles.clear()
        self.addInputFile("run.sh")
        
    def removeInputFile(self, inputFile):
        try:
            del(self.__inputFiles[inputFile])
        except:
            pass
        
    def addOutputFile(self, outputFile, url=""):
        self.__outputFile[outputFile] = url
        
    def clearOutputFiles(self):
        self.__outputFiles[:] = []
        
    def addCluster(self, cluster):
        self.__clusters.append(cluster)
        
    def clearClusters(self):
        self.__clusters[:] = []
        
    def tagAsExecutable(self, filename):
        if self.__inputFiles.has_key(filename):
            self.__executables.append(filename)
            
    def clearExecutableTags(self):
        self.__executables[:] = []
        
    def addRuntimeEnvironment(self, runtimeEnvironment):
        self.__runtimeEnvironments.append(runtimeEnvironment)
        
    def clearRuntimeEnvironments(self):
        self.__runtimeEnvironments[:] = []
        
    def __setstate__(self, state):
        # Add version attribute to task
        if '__version' not in state:
            self.__version = "1.0"
        self.doUpdateState(state, self.__version)
        self.__dict__.update(state)
        
    def doUpdateState(self, state, version):
        """Add or remove task attributes that has changed from
        the version loaded from disk."""
        pass
        
    def setup(self):
        self.doSetupTaskDirs()
        
    def clean(self):
        self.doCleanTaskDirs()
        
    def getJobList(self):
        """
        Return a list of job descriptions and directories
        """
        jobList = []
        for i in range(self.sweepSize):
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            
            jobDescription = self.doCreateJobDescription(taskName, taskId, taskDir)
            jobList.append(jobDescription)

        return jobList
           
    def _existInList(self, stringList, pattern):
        for line in stringtList:
            if line.find(pattern)>=0:
                return True
        return False
           
    def doSetupTaskDirs(self):
        
        taskIds = range(self.sweepSize)
        
        for i in range(self.sweepSize):
            
            # Create task dir
            
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            if not os.path.exists(taskDir):
                os.mkdir(taskDir)
                
            # Create run-script
            
            runScriptTemplate = self.doCreateRunScript(taskName, taskId)
            runScriptFile = open(os.path.join(self.workDir, "run.sh"), "w")
            runScriptFile.write(runScriptTemplate)
            runScriptFile.close()
                
            # Copy files to task dir
            
            for filename in self.__inputFiles.keys():
                url = self.__inputFiles[filename]
                if url=="":
                    fullPath = os.path.join(self.workDir, filename)
                    destPath = os.path.join(taskDir, filename)
                    
                    # Do parameter replacement
                    
                    templateFile = open(fullPath, "r")
                    templateString = templateFile.read()
                    if templateString.find(r'%(name)s')!=-1:
                        templateString = self.doAssignTemplateName(templateString, self.name)
                    if templateString.find(r'%(id)d')!=-1:
                        templateString = self.doAssignTemplateId(templateString, taskId)
                    if templateString.find(r'%(sweepSize)d')!=-1:
                        templateString = self.doAssignTemplateSweepSize(templateString, self.sweepSize)
                    if templateString.find(r'%(value)g')!=-1:
                        taskValue = self.doCalculateSweepValueFloat(taskId, self.sweepSize)
                        templateString = self.doAssignTemplateValue(templateString, taskValue)
                    if templateString.find(r'%(value)d')!=-1:
                        taskValue = self.doCalculateSweepValueInt(taskId, self.sweepSize)
                        templateString = self.doAssignTemplateValue(templateString, taskValue)
                    templateFile.close()
                    
                    # Write template file
                    
                    if os.path.isfile(fullPath):
                        templateFile = open(destPath, "w")
                        templateFile.write(templateString)
                        templateFile.close()
                        
    def doCleanTaskDirs(self):

        taskIds = range(self.sweepSize)
        
        for i in range(self.sweepSize):
            
            # Create task dir
            
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            
            if os.path.exists(taskDir):
                print "rmtree(%s)" % taskDir
                shutil.rmtree(taskDir)
    
    def doAssignTemplateName(self, templateString, taskName):
        return templateString.replace(r'%(name)s', taskName)
    
    def doAssignTemplateId(self, templateString, taskId):
        return templateString.replace(r'%(id)d', str(taskId))
        
    def doAssignTemplateSweepSize(self, templateString, sweepSize):
        return templateString.replace(r'%(sweepSize)d', str(sweepSize))
    
    def doAssignTemplateValue(self, templateString, taskValue):
        return templateString.replace(r'%(value)d', str(taskValue))

    def doCalculateSweepValueFloat(self, taskId, sweepSize):
        if self.calculateSweepValueFloat!=None:
            return self.calculateSweepValueFloat(taskId, sweepSize)
        else:
            return float(taskId)
    
    def doCalculateSweepValueInt(self, taskId, sweepSize):
        if self.calculateSweepValueInt!=None:
            return self.calculateSweepValueInt(taskId, sweepSize)
        else:
            return float(taskId)
            
    def doCreateRunScript(self, taskName, taskId):
        """
        Abstract routine responsible for returning a
        run-script for the job.
        """
        return ""

    def doSetupScripts(self):
        """Abstract routine responsible for creating the
        necessary files that make up the grid task, such
        as scripts, XRSL and input files."""
        pass

    def doClean(self):
        """Abstract routine responsible for cleaning any
        temporay files created by the setup() routine."""
        pass
    
    def doRefresh(self):
        """If any new attributes are added in new versions of
        a task the refresh method is responsible for checking
        for these and adding/removing them if they do not exist."""
        pass
    
    def doCreateJobDescription(self, taskName, taskId, taskDir):
        """
        Abstract routines responsible for returning a jobdescription for
        the job.
        """
        return None
    
    def getInputFiles(self):
        return self.__inputFiles
    
    def getOutputFiles(self):
        return self.__outputFiles
    
    def getRuntimeEnvironments(self):
        return self.__runtimeEnvironments
    
    def getClusters(self):
        return self.__clusters
    
    def getExecutables(self):
        return self.__executables
    
    def getSweepParams(self):
        return self.__sweepParams
        
    inputFiles = property(getInputFiles)
    outputFiles = property(getOutputFiles)
    runtimeEnvironments = property(getRuntimeEnvironments)
    clusters = property(getClusters)
    executables = property(getExecutables)
    sweepParams = property(getSweepParams)
    
class LapBaseTask(BaseTask):
    def __init__(self):
        BaseTask.__init__(self)
        self.taskEditPage = ""
        
    def getTaskEditPage(self):
        return self.taskEditPage
            
        
class Task:
    """Grid task base class.
    
    Manages a typical grid task. Consists of
    a set of XRSL attributes and application specific attributes.
    """
    def __init__(self):
        """Class constructor."""
        self.xrslAttributes = XRSLAttributes()
        self.remoteExecutable = False
        self.description = "Default LAP task"
        self.attributes = {}
        self.taskDir = ""
        self.taskEditPage = ""
        self.customXRSLGeneration = False
        self.specialFiles = {}
        
        self.__version = "1.0"
        
        self.refresh()
        
    def __setstate__(self, state):
        # Add version attribute to task
        if '__version' not in state:
            self.__version = 1.0
        self.doUpdateState(state, self.__version)
        self.__dict__.update(state)
        
    def doUpdateState(self, state, version):
        """Add or remove task attributes that has changed from
        the version loaded from disk."""
        pass

    def setup(self):
        """Abstract routine responsible for creating the
        necessary files that make up the grid task, such
        as scripts, XRSL and input files."""
        pass

    def clean(self):
        """Abstract routine responsible for cleaning any
        temporay files created by the setup() routine."""
        pass
    
    def refresh(self):
        """If any new attributes are added in new versions of
        a task the refresh method is responsible for checking
        for these and adding/removing them if they do not exist."""
        pass
    
    def setDescription(self, description):
        """Sets the task description."""
        self.description = description

    def getDescription(self):
        """Returns task description."""
        return self.description

    def setJobName(self, name):
        """Set job name (XRSL)."""
        self.xrslAttributes["jobName"] = name

    def getJobName(self):
        """Return job name (XRSL)."""
        return self.xrslAttributes["jobName"]

    def setCpuTime(self, cpuTime):
        """Set cpu time (XRSL)."""
        self.xrslAttributes["cpuTime"] = cpuTime

    def setEmail(self, email):
        """Set task email (XRSL)."""
        self.xrslAttributes["notify"] = email
        
    def setTaskEditPage(self, page):
        """Set the page which is used to edit this task."""
        self.taskEditPage = page
        
    def getTaskEditPage(self):
        """Return page for editing this task."""
        return self.taskEditPage
    
    def clearExecutableTags(self):
        """Clear executables tag."""
        self.xrslAttributes["executables"] = ""
    
    def tagAsExecutable(self, executableName):
        """Tag an input file as executable."""
        if not self.xrslAttributes.has_key("executables"):
            self.xrslAttributes["executables"] = ""
        self.xrslAttributes["executables"] = self.xrslAttributes["executables"] + executableName + " "
        
    def addInputFile(self, name, location=""):
        """Add an input file to the task.
        
        @type name: string
        @param name: filename of input file.
        @type location: string
        @param location: URL of the input file. If empty the
        file is considered local."""
        self.xrslAttributes["inputFiles"][name] = location
        
    def clearInputFiles(self):
        """Clear the list of input files."""
        self.xrslAttributes["inputFiles"] = {}

    def addOutputFile(self, name, location=""):
        """Add an input file to the task.
        
        @type name: string
        @param name: filename of input file.
        @type location: string
        @param location: URL where to store the outputfile. If empty the
        file is downloaded to the local directory."""
        self.xrslAttributes["outputFiles"][name] = location
        
    def clearOutputFiles(self):
        """Clear the list of output files."""
        self.xrslAttributes["outputFiles"] = {}

    def getInputFiles(self):
        """Return list of input files."""
        return self.xrslAttributes["inputFiles"]
    
    def setDir(self, taskDir):
        """Set the task directory"""
        self.taskDir = taskDir

    def getDir(self):
        """Return the directory of the task."""
        return self.taskDir

    def getXRSLAttributes(self):
        """Return XRSL property list."""
        return self.xrslAttributes

    def getAttributes(self):
        """Return application specific property list."""
        return self.attributes

    def printAttributes(self):
        """Print the application specific properties."""
        for key in self.parameters.keys():
            print key + " = " + str(self.parameters[key])


class TaskDescriptionFile:
    """Task description class.
    
    This class represents an abstract base class for a task
    description file."""
    def __init__(self, task):
        """Class constructor.
        
        @type task: Task
        @param task: Task instance associated with the description file."""
        self.task = task
        self.filename = ""

    def setFilename(self, name):
        """Set filename of the task description file."""
        self.filename = name

    def getFilename(self):
        """Return the filename of the task description file."""
        return self.filename

    def setTask(self, task):
        """Assign a new task to the task description file."""
        self.task = task

    def getTask(self):
        """Return Task instance."""
        return self.task

    def write(self):
        """Abstract method responsible for writing the task
        description in some kind of description language."""
        pass

class XRSLFile(TaskDescriptionFile):
    """XRSL task description file class
    
    This class is responsible for converting a Task instance into
    a XRSL description."""
    def __init__(self, task):
        """Class constructor.
        
        @type task: Task
        @param task: Task instance associated with the description file."""
        TaskDescriptionFile.__init__(self, task)
        self._reOperator = ">="

    def setReVersionOperator(self, operator):
        """Set the operator used for querying for runtime-environments.
        This operator is default set to >=, accepting RE:s with equal or
        higher version numbers than specified. If set to = only RE versions
        number matching the exactly will be accepted."""
        self._reOperator = operator

    def write(self):
        """Write XRSL task description to file."""
        if self.getFilename()!="" and self.getTask()!=None:
            xrslFile = open(self.getFilename(), 'w')
            xrslFile.write("&\n")

            for key, value in self.getTask().getXRSLAttributes().items():
                
                print key, " = ", value
                
                operator = "="

                if key == "runTimeEnvironment":
                    operator = self._reOperator

                haveValue = False

                if type(value) is str:
                    if type(value) is str:
                        if key == "executables":
                            if value!="":
                                xrslFile.write('(' + key + ' '+operator+' ' + value + ')\n')
                        else:
                            if value!="":
                                xrslFile.write('(' + key + ' '+operator+' "' + value + '")\n')
                elif type(value) is int:
                    if value!=-1:
                        xrslFile.write("(" + key + " "+operator+" " + repr(value) + ")\n")
                elif type(value) is dict:
                    xrslFile.write('(' + key + ' = \n')
                    for key2, value2 in value.items():
                        print key2, ", ", value2
                        xrslFile.write('\t("' + key2 + '" "' + value2 + '")\n')
                    xrslFile.write(')\n')
                    

            xrslFile.close()
            
class XRSLWriter(TaskDescriptionFile):
    """XRSL write class.
    
    This class can be used to write XRSL descriptions consisting of
    several XRSL attribute descriptions concatenated together using the
    & operator."""
    def __init__(self):
        """Class constructor."""
        self._attribs = []
        self._filename = ""
        self._reOperator = ">="
        
    def setFilename(self, filename):
        """Set XRSL output filename."""
        self._filename = filename
        
    def getFilename(self):
        """Return XRSL output filename."""
        return self._filename
    
    def addXRSLAttributes(self, attribs):
        """Add XRSL property list"""
        self._attribs.append(attribs)
        
    def setReVersionOperator(self, operator):
        """Set the operator used for querying for runtime-environments.
        This operator is default set to >=, accepting RE:s with equal or
        higher version numbers than specified. If set to = only RE versions
        number matching the exactly will be accepted."""
        self._reOperator = operator

    def write(self):
        """Write XRSL task description to file."""
        if self.getFilename()!="" and self._attribs!=None:
            
            xrslFile = open(self.getFilename(), 'w')
            
            xrslFile.write("+\n")

            for attribs in self._attribs:
                
                xrslFile.write("(\n")
                xrslFile.write("&\n")

                for key, value in attribs.items():
    
                    haveValue = False
                    
                    operator = "="
                    
                    if key == "runTimeEnvironment":
                        operator = self._reOperator
    
                    if type(value) is str:
                        if key == "executables":
                            if value!="":
                                xrslFile.write('(' + key + ' '+operator+' ' + value + ')\n')
                        else:
                            if value!="":
                                xrslFile.write('(' + key + ' '+operator+' "' + value + '")\n')
                    elif type(value) is int:
                        if value!=-1:
                            xrslFile.write("(" + key + " "+operator+" " + repr(value) + ")\n")
                    elif type(value) is dict:
                        xrslFile.write('(' + key + ' = \n')
                        for key2, value2 in value.items():
                            print key2, ", ", value2
                            xrslFile.write('\t("' + key2 + '" "' + value2 + '")\n')
                        xrslFile.write(')\n')
                        
                xrslFile.write(")\n")

            xrslFile.close()        
        
def taskFactory(*pargs, **kargs):
    #obj = jsMenuBar(*pargs, **kargs)
    obj = BaseTask(*pargs, **kargs)
    return obj
