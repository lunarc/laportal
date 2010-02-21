#!/bin/env python

import os, sys, string, shutil

import ConfigParser

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
        self.version = "1.0"
        self.taskType = "BaseTask"
        self.groupSerial = 0
        
        self.dirty = False
        
        self.workDir="."
    
        self.sweepSize = 1
        self.__sweepParams = {"taskid":-1}
        self.__sweepFiles = {}
        
        self.calculateSweepValueFloat = None
        self.calculateSweepValueInt = None
        
        self.addInputFile("run.sh")
               
    def addInputFile(self, inputFile, url=""):
        self.__inputFiles[inputFile] = url
        
    def addAndCopyInputFile(self, inputFile, copyFile = True):
        """
        Add and copy input files to task workdir.
        """
        if os.path.exists(inputFile) and os.path.exists(self.workDir):
            head, tail = os.path.split(inputFile)
            if copyFile:
                shutil.copy(inputFile, self.workDir)
            self.addInputFile(tail)
            return True
        else:
            return False
        
    def clearInputFiles(self):
        self.__inputFiles.clear()
        self.addInputFile("run.sh")
        
    def removeInputFile(self, inputFile):
        try:
            del(self.__inputFiles[inputFile])
        except:
            pass
        
    def addSweepFile(self, sweepFile):
        self.__sweepFiles[sweepFile] = ""
        
    def clearSweepFiles(self):
        self.__sweepFiles.clear()
        
    def removeSweepFile(self, sweepFile):
        if self.__sweepFiles.has_key(sweepFile):
            del self.__sweepFiles[sweepFile]
        
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
        self.onUpdateState(state, self.__version)
        self.__dict__.update(state)
        
    def onUpdateState(self, state, version):
        """Add or remove task attributes that has changed from
        the version loaded from disk."""
        pass
        
    def setup(self):
        self.onSetupTaskDirs()
        
    def clean(self):
        self.onCleanTaskDirs()
        
    def __saveDefaultConfig(self, config):
        config.add_section("task")
        config.set("task", "type", self.taskType)
        config.set("task", "version", self.version)

        config.add_section("general")
        config.set("general", "name", self.name)
        config.set("general", "description", self.description)
        config.set("general", "executable", self.executable)
        config.set("general", "arguments", self.arguments)
        config.set("general", "cputime", str(self.cpuTime))
        config.set("general", "notify", self.notify)
        config.set("general", "memory", str(self.memory))
        config.set("general", "disk", str(self.disk))
        config.set("general", "stdin", self.stdin)
        config.set("general", "stdout", self.stdout)
        config.set("general", "stderr", self.stderr)
        config.set("general", "logging", str(self.logging))
        config.set("general", "count", str(self.count))

        config.add_section("params")
        config.set("params", "sweepSize", str(self.sweepSize))

        count = 0
        
        for sweepFile in self.sweepFiles.keys():
            config.set("params", "sweepfile_%d" % count, sweepFile)
            count += 1

        config.add_section("inputfiles")
        
        count = 0
        
        for inputFile in self.inputFiles.keys():
            config.set("inputfiles", "inputfile_%d" % count, inputFile)
            count += 1

    def __loadDefaultConfig(self, config):
        try:
            self.taskType = config.get("task", "type")
            self.version = config.get("task", "version")
            self.name = config.get("general", "name")
            self.description = config.get("general", "description")
            self.executable = config.get("general", "executable")
            self.arguments = config.get("general", "arguments")
            self.cpuTime = int(config.get("general", "cputime",))
            self.notify = config.get("general", "notify")
            self.memory = int(config.get("general", "memory"))
            self.disk = int(config.get("general", "disk"))
            self.stdin = config.get("general", "stdin")
            self.stdout = config.get("general", "stdout")
            self.stderr = config.get("general", "stderr")
            self.logging = bool(config.get("general", "logging"))
            self.count = int(config.get("general", "count"))
            self.sweepSize = int(config.get("params", "sweepsize"))
            
            count = 0
                
            while config.has_option("inputfiles", "inputfile_%d" % count):
                inputFile = config.get("inputfiles", "inputfile_%d" % count)
                self.addInputFile(inputFile)
                count += 1

            count = 0
                
            while config.has_option("params", "sweepfile_%d" % count):
                sweepFile = config.get("params", "sweepfile_%d" % count)
                self.addSweepFile(sweepFile)
                count += 1
        except:
            pass
        
    def save(self):
        configFilename = os.path.join(self.workDir, "%s.ini" % self.name)
        configParser = ConfigParser.ConfigParser()
        self.__saveDefaultConfig(configParser)
        self.onSaveConfig(configParser)
        
        configFile = open(configFilename, "w")
        configParser.write(configFile)
        configFile.close()
        
        self.dirty = False
    
    def load(self):
        configFilename = os.path.join(self.workDir, "%s.ini" % self.name)
        configFile = open(configFilename, "r")
        configParser = ConfigParser.ConfigParser()
        configParser.readfp(configFile)
        configFile.close()
        
        self.__loadDefaultConfig(configParser)
        self.onLoadConfig(configParser)
        
        self.dirty = False
    
    def onSaveConfig(self, config):
        pass
    
    def onLoadConfig(self, config):
        pass
        
    def getJobList(self):
        """
        Return a list of job descriptions and directories
        """
        jobList = []
        for i in range(self.sweepSize):
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            
            jobDescription = self.onCreateJobDescription(taskName, taskId, taskDir)
            jobList.append(jobDescription)

        return jobList
    
    def getJobInfo(self):
        """
        Return a list of job directories
        """
        jobInfo = []
        for i in range(self.sweepSize):
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            
            jobInfo.append([taskName, taskId, taskDir])

        return jobInfo
        
           
    def _existInList(self, stringList, pattern):
        for line in stringtList:
            if line.find(pattern)>=0:
                return True
        return False
           
    def onSetupTaskDirs(self):
        
        taskIds = range(self.sweepSize)
        
        for i in range(self.sweepSize):
            
            # Create task dir
            
            taskName=self.name+"_%04d" % (i+1)
            taskId = i+1
            taskDir = os.path.join(self.workDir,taskName)
            if not os.path.exists(taskDir):
                os.mkdir(taskDir)
                
            # Create run-script
            
            runScriptTemplate = self.onCreateRunScript(taskName, taskId)
            runScriptFile = open(os.path.join(self.workDir, "run.sh"), "w")
            runScriptFile.write(runScriptTemplate)
            runScriptFile.close()
                
            # Copy files to task dir
            
            for filename in self.__inputFiles.keys():
                url = self.__inputFiles[filename]
                if url=="":
                    fullPath = os.path.join(self.workDir, filename)
                    destPath = os.path.join(taskDir, filename)
                    
                    if self.__sweepFiles.has_key(filename):
                                       
                        # Do parameter replacement
                                           
                        templateFile = open(fullPath, "r")
                        templateString = templateFile.read()
                        if templateString.find(r'%(name)s')!=-1:
                            templateString = self.onAssignTemplateName(templateString, self.name)
                        if templateString.find(r'%(id)d')!=-1:
                            templateString = self.onAssignTemplateId(templateString, taskId)
                        if templateString.find(r'%(sweepSize)d')!=-1:
                            templateString = self.onAssignTemplateSweepSize(templateString, self.sweepSize)
                        if templateString.find(r'%(value)g')!=-1:
                            taskValue = self.doCalculateSweepValueFloat(taskId, self.sweepSize)
                            templateString = self.onAssignTemplateValue(templateString, taskValue)
                        if templateString.find(r'%(value)d')!=-1:
                            taskValue = self.doCalculateSweepValueInt(taskId, self.sweepSize)
                            templateString = self.onAssignTemplateValue(templateString, taskValue)
                        templateFile.close()
                        
                        # Write template file
                        
                        if os.path.isfile(fullPath):
                            templateFile = open(destPath, "w")
                            templateFile.write(templateString)
                            templateFile.close()
                    else:
                        
                        # Just copy the file.
                        
                        shutil.copy(fullPath, destPath)
                        
                        
    def onCleanTaskDirs(self):
        
        dirList = os.listdir(os.path.join(self.workDir))
        
        for dirItem in dirList:
            fullPath = os.path.join(self.workDir, dirItem)
            if os.path.isdir(fullPath):
                if fullPath.find(self.name+"_")!=-1:
                    shutil.rmtree(fullPath)
    
    def onAssignTemplateName(self, templateString, taskName):
        return templateString.replace(r'%(name)s', taskName)
    
    def onAssignTemplateId(self, templateString, taskId):
        return templateString.replace(r'%(id)d', str(taskId))
        
    def onAssignTemplateSweepSize(self, templateString, sweepSize):
        return templateString.replace(r'%(sweepSize)d', str(sweepSize))
    
    def onAssignTemplateValue(self, templateString, taskValue):
        return templateString.replace(r'%(value)d', str(taskValue))

    def onCalculateSweepValueFloat(self, taskId, sweepSize):
        if self.calculateSweepValueFloat!=None:
            return self.calculateSweepValueFloat(taskId, sweepSize)
        else:
            return float(taskId)
    
    def onCalculateSweepValueInt(self, taskId, sweepSize):
        if self.calculateSweepValueInt!=None:
            return self.calculateSweepValueInt(taskId, sweepSize)
        else:
            return float(taskId)
            
    def onCreateRunScript(self, taskName, taskId):
        """
        Abstract routine responsible for returning a
        run-script for the job.
        """
        return ""

    def onSetupScripts(self):
        """Abstract routine responsible for creating the
        necessary files that make up the grid task, such
        as scripts, XRSL and input files."""
        pass

    def onClean(self):
        """Abstract routine responsible for cleaning any
        temporay files created by the setup() routine."""
        pass
    
    def onRefresh(self):
        """If any new attributes are added in new versions of
        a task the refresh method is responsible for checking
        for these and adding/removing them if they do not exist."""
        pass
    
    def onCreateJobDescription(self, taskName, taskId, taskDir):
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
    
    def getSweepFiles(self):
        return self.__sweepFiles
        
    inputFiles = property(getInputFiles)
    outputFiles = property(getOutputFiles)
    runtimeEnvironments = property(getRuntimeEnvironments)
    clusters = property(getClusters)
    executables = property(getExecutables)
    sweepParams = property(getSweepParams)
    sweepFiles = property(getSweepFiles)
    jobList = property(getJobList)
    jobInfo = property(getJobInfo)