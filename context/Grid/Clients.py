#!/usr/bin/python

#
# Clients - Wrapper class for the libarclient library.
#
# Copyright (C) 2008-2009 Jonas Lindemann
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

"""
Class wrappers for grid client libraries.
"""

import arc, sys, os;

class ManagedJobDescription(arc.JobDescription):
    """
    Class for making job description handling easier.
    """
    def __init__(self):
        """
        Class constructor
        """
        arc.JobDescription.__init__(self)

    def addArgument(self, argument):
        """
        Add argument description.
        """
        self.Argument.append(argument)
    
    def addInputFile(self, name, url="", keepData = True, isExecutable = False, downloadToCache = False, threads = -1):
        """
        Add an input file, name, to the job description.
        """
        inputFile = arc.FileType()
        inputFile.Name = os.path.basename(name)
        inputFile.KeepData = False
        inputFile.IsExecutable = False
        inputFile.DownloadToCache = False
        inputFileSource = arc.SourceType()
        if url=="":
            fullPath = os.path.abspath(name)
            urlRepr = "file://"+fullPath
            inputFileSource.URI = arc.URL(urlRepr)
        else:
            inputFileSource.URI = arc.URL(url)
        inputFileSource.Threads = threads
        inputFile.Source.append(inputFileSource)
        self.File.append(inputFile)
        
    def clearInputFiles(self):
        """
        Clear input files.
        """
        pass
    
    def addOutputFile(self, name, url="", keepData = True, isExecutable = False, downloadToCache = False, threads = -1):
        """
        Add outputfile to job description.
        """
        outputFile = arc.FileType()
        outputFile.Name = name
        outputFile.KeepData = False
        outputFile.IsExecutable = False
        outputFile.DownloadToCache = False
        outputFileTarget = arc.TargetType()
        outputFileTarget.URI = arc.URL(url)
        outputFileTarget.Threads = threads
        outputFileTarget.Mandatory = True
        outputFile.Target.append(outputFileTarget)
        self.File.append(outputFile)
        
    def clearOutputFiles(self):
        """
        Clear output files.
        """
        pass
    
    def addRuntimeEnvironment(self, name, version):
        """
        Add a runtime environment and version.
        """
        runtimeEnv = arc.RunTimeEnvironmentType()
        runtimeEnv.Name = name
        runtimeEnv.Version.append(version)
        self.RunTimeEnvironment.append(runtimeEnv)
        
        
class ArcClient(object):
    
    # Setup ARC logging
    
    loggerConfigured = False
    persistentLogger = None
   
    def __init__(self, proxyFilename = "./proxy.pem", jobListFilename="./jobs.xml", userConfigFilename = "./client.xml", logFilename=""):
        """
        ArcClient class constructor
        
        Initialises properties and variables, sets up logging and
        loads job list.
        """
        
        # Setup class properties
        
        self.jobListFilename = jobListFilename
        self.userConfigFilename = userConfigFilename
        self.__proxyFilename = proxyFilename
        self.downloadDir = "."
        
        # Setup user configuration
        
        self.userConfig = arc.UserConfig(self.userConfigFilename, self.jobListFilename, False)

        if self.userConfig.ConfTree().Get("CACertificatePath")=="":
            self.userConfig.ConfTree().NewChild("CACertificatePath").Set("/etc/grid-certificates")
            
        if self.userConfig.ConfTree().Get("CertificatePath")=="":
            self.userConfig.ConfTree().NewChild("CertificatePath").Set(proxyFilename)
            
        if self.userConfig.ConfTree().Get("KeyPath")=="":
            self.userConfig.ConfTree().NewChild("KeyPath").Set(proxyFilename)
            
        if self.userConfig.ConfTree().Get("ProxyPath")=="":
            self.userConfig.ConfTree().NewChild("ProxyPath").Set(proxyFilename)
                
        self.userConfig.ConfTree().SaveToFile(userConfigFilename)
        
        self.userConfig.InitializeCredentials()
        self.userConfig.CheckProxy()
                           
        self.targets = []
        self.filteredTargets = []
        self.jobList = None
        self.jobDict = {}
        self.clusters = []
        self.__debugLevel = arc.DEBUG
        self.__doFiltering = True
        self.updateProgress = None
        
        self.__logFilename = logFilename
        
        # Setup ARC logging
        
        if self.__logFilename!="":
            self.__logStream = self
        else:
            self.__logStream = None
        
        if self.__logStream==None:
            self.__logStream = sys.stdout
        
        logcout = arc.LogStream(self.__logStream)
        arc.Logger_getRootLogger().removeDestinations()       
        arc.Logger_getRootLogger().addDestination(logcout)
        arc.Logger_getRootLogger().setThreshold(self.__debugLevel)
        
        # Setup ACC loader
        
        self.__loaderConfig = arc.Config(arc.NS())
        arc.ACCConfig().MakeConfig(self.__loaderConfig)
        self.__loader = arc.ACCLoader(self.__loaderConfig)
        
        self.__targetGenerator = arc.TargetGenerator(self.userConfig, [], []);
        
        # Initialise joblist
        
        self.__loadJobs()
        
    def setLogStream(self, stream):
        """
        Assigns a log stream to libarclib
        """
        self.__logStream = stream
        logcout = arc.LogStream(stream);
        arc.Logger_getRootLogger().removeDestinations()
        arc.Logger_getRootLogger().addDestination(logcout)

    def getLogStream(self,):
        """
        Returns currently used log stream. (Default=None)
        """
        return self.__logStream

    def setDebugLevel(self, level):
        """
        Set debug level of the arc library.
        """
        self.__debugLevel = level
        arc.Logger_getRootLogger().setThreshold(self.__debugLevel);
    
    def getDebugLevel(self):
        """
        Return the debug level of the arc library.
        """
        return self.__debugLevel
    
    def setProxyFilename(self, filename):
        """
        Set the proxy filename.
        """
        self.__proxyFilename = filename
        
    def getProxyFilename(self):
        """
        Returns the proxy filename.
        """
        return self.__proxyFilename
    
    def setLogFilename(self, filename):
        """
        Assign filename to redirect the libarcclient log stream. Stream
        is automatically redirected.
        """
        self.__logFilename = filename
        self.logStream = self
        
    def getLogFilename(self):
        """
        Return current log filename.
        """
        return self.__logFilename
    
    def write(self, output):
        """
        Make the ARC client redirect logging from arc to a file.
        """
        
        # Check for locking solution.
        
        logFile = open(self.__logFilename, "a")
        logFile.write(output)
        logFile.close()
        
    def readLog(self):
        """
        Reads the log file, if any, and returns
        a list with log items.
        """
        
        if self.__logFilename!="":
            if os.path.exists(self.__logFilename):
                
                logList = []
                
                logFile = open(self.__logFilename, "r")
                logLines = logFile.readlines()
                logFile.close()
                
                for line in logLines:
                    parts = line.split("] [")
                    logTime = parts[0][1:]
                    logComponent = parts[1]
                    logLevel = parts[2]
                    logMessage = parts[3].split("] ")[1]
                    logList.append([logTime, logComponent, logLevel, logMessage])
                
                return logList
        return []
        
    def clearLog(self):
        """
        Clears the log file.
        """
        logFile = open(self.__logFilename, "w")
        logFile.close()
    
    def saveConfiguration(self):
        """
        Saves the libarclient XML configuration file.
        """
        self.userConfig.ConfTree().SaveToFile(self.userConfigFilename)
    
    def __loadJobs(self):
        """
        Load job list from XML file.
        """
        self.jobList = arc.Config(arc.NS())
        if os.path.exists(self.jobListFilename):
            self.jobList.ReadFromFile(self.jobListFilename)
            self.jobDict.clear()
            for j in self.jobList.Path("Job"):
                self.jobDict[str(j.Get("JobID"))]= {}
                self.jobDict[str(j.Get("JobID"))]= {"Name":j.Get("Name")}
                
    def loadJobList(self):
        """
        Loads job list from file.
        """
        self.__loadJobs()
                
    def hasValidProxy(self):
        """
        Returns True if proxy is valid.
        """
        return self.userConfig.CheckProxy()

    def findTargets(self):
        """
        Find possible targets by querying information system.
        """
        
        self.doProgress("Finding suitable targets.")
        
        #self.userConfig.ConfTree().SaveToFile("test1.xml")
        
        self.targets = None
        self.__targetGenerator.GetTargets(0, 1);
        self.targets = self.__targetGenerator.ModifyFoundTargets()
        
    def loadBroker(self, brokerName="RandomBroker"):
        """
        Wrapper function for encapsulating ARC1 loading of
        of a broker instance.
        """
        
        return self.__loader.loadBroker(brokerName, self.userConfig)
        
    def filterTargets(self, job):
        """
        Return a filtered list of suitable targets based on the
        RandomBroker component.
        """
        if self.__doFiltering:
    
            self.doProgress("Prefiltering targets.")
    
            self.chosenBroker = self.__loader.loadBroker("RandomBroker", self.userConfig.ConfTree())
            self.chosenBroker.PreFilterTargets(self.targets, job)
            
            self.doProgress("Finding best target.")
            
            target = self.chosenBroker.GetBestTarget()
            while not target==None:
                target = self.chosenBroker.GetBestTarget()
                if target!=None:
                    self.filteredTargets.append(target)
            
            return self.filteredTargets
        else:
            del(self.filteredTargets[:])

            for target in self.targets:
                if target.ServiceName=="siri.lunarc.lu.se":
                    self.filteredTargets.append(target)
            
            return self.filteredTargets

    def submit(self, job):
        """
        Submit job to grid. Requires that a list of filtered targets
        exists.
        """
        self.doProgress("Submitting job.")

        if len(self.filteredTargets)==0:
            return False
        
        target = self.filteredTargets[0]
        
        info = arc.XMLNode(arc.NS(), 'Jobs')
                
        self.submitter = target.GetSubmitter(self.userConfig)
        submitted = self.submitter.Submit(job, self.jobListFilename)
        
        if submitted:
            self.doProgress("Updating job file.")
            self.__loadJobs()
            return True
        else:
            return False
            
    def loadJobController(self):
        """
        Wrapper function for loading a JobController instance.
        """
        accConfig  = arc.ACCConfig()
        loaderConfig = arc.Config(arc.NS())
        accConfig.MakeConfig(loaderConfig)
        
        controllerCfg = loaderConfig.NewChild("ArcClientComponent")
        controllerCfg.NewAttribute("name").Set("JobControllerARC0")
        controllerCfg.NewAttribute("id").Set("jobController")
        self.userConfig.ApplySecurity(controllerCfg)
        self.userConfig.ApplyTimeout(controllerCfg)
            
        loader = arc.ACCLoader(loaderConfig)
        
        # ATT: Must be added to client.i
        jobController = loader.getJobController("jobController")
        
        return jobController
            
    def get(self, jobIds = [], status = ["FINISHED", "FAILED"], keep=False):
        """
        Download results from jobs.
        """
        
        #Arc::XMLNode jobctrl = cfg.NewChild("ArcClientComponent");
        #jobctrl.NewAttribute("name") = "JobControllerARC0";
        #jobctrl.NewAttribute("id") = "controller";
        #usercfg.ApplySecurity(jobctrl);
        #jobctrl.NewChild("JobList") = joblist;
        #  
        #//prepare loader
        #
        #Arc::ACCLoader *loader = new Arc::ACCLoader(cfg);
        #  
        #//load a JobControllerARC0
        #Arc::JobController *jobcontroller =
        #  dynamic_cast<Arc::JobController*>(loader->getACC("controller"));
        
        self.doProgress("Retrieving job controllers.")
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds, self.clusters, self.jobListFilename);
        jobControllers = jobSupervisor.GetJobControllers()
        
        for controller in jobControllers:
            self.doProgress("Retrieving job.")
            controller.Get(status, str(self.downloadDir), keep)
            
        self.doProgress("Done.")
            
        self.__loadJobs()
        
    def kill(self, jobIds = [], status = [], force = False):
        """
        Kill running jobs.
        """
        
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds, self.clusters, self.jobListFilename);
        jobControllers = jobSupervisor.GetJobControllers();
        
        for controller in jobControllers:
            controller.Kill(status, force);
        
        self.__loadJobs()
        
    def clean(self, jobIds = [], status = [], force = False):
        """
        Clean running jobs.
        """
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds, self.clusters, self.jobListFilename);
        jobControllers = jobSupervisor.GetJobControllers();
        
        for controller in jobControllers:
            controller.Clean(status, force);
        
        self.__loadJobs()

    def doProgress(self, message):
        """
        Call progress update callback if assigned otherwise
        ignore.
        
        message - Message to pass to progress callback function.
        """
        if self.updateProgress!=None:
            self.updateProgress(message)
                
    def updateStatus(self):
        """
        Query information system and populate the jobs property with additional
        job information.
        """
        
        self.doProgress("Creating job supervisor.")
        
        jobSupervisor = arc.JobSupervisor(self.userConfig, [], [], self.jobListFilename)        
        jobControllers = jobSupervisor.GetJobControllers();
        
        self.doProgress("Querying job controllers")
               
        for controller in jobControllers:
            self.doProgress("Getting job information.")
            controller.GetJobInformation()
            self.doProgress("Extracting job information.")
            jobStore = controller.GetJobs()
            for job in jobStore:
                jobId = job.JobID.str()
                jobState = job.State
                if self.jobDict.has_key(jobId):
                    try:
                        self.jobDict[jobId]["State"] = jobState()
                        self.jobDict[jobId]["Name"] = job.Name
                        self.jobDict[jobId]["Type"] = job.Type
                        self.jobDict[jobId]["JobDescription"] = job.JobDescription
                        self.jobDict[jobId]["ExitCode"] = job.ExitCode
                        self.jobDict[jobId]["UserDomain"] = job.UserDomain
                        self.jobDict[jobId]["LocalIdFromManager"] = job.LocalIdFromManager
                        self.jobDict[jobId]["Owner"] = job.Owner
                        self.jobDict[jobId]["WaitingPosition"] = job.WaitingPosition
                        self.jobDict[jobId]["LocalOwner"] = job.LocalOwner
                        self.jobDict[jobId]["RequestedMainMemory"] = job.RequestedMainMemory
                        self.jobDict[jobId]["RequestedSlots"] = job.RequestedSlots
                        self.jobDict[jobId]["StdIn"] = job.StdIn
                        self.jobDict[jobId]["StdOut"] = job.StdOut
                        self.jobDict[jobId]["StdErr"] = job.StdErr
                        self.jobDict[jobId]["LogDir"] = job.LogDir
                        self.jobDict[jobId]["ExecutionCE"] = job.ExecutionCE
                        self.jobDict[jobId]["Queue"] = job.Queue
                        self.jobDict[jobId]["UsedMainMemory"] = job.UsedMainMemory
                        self.jobDict[jobId]["UsedSlots"] = job.UsedSlots
                        self.jobDict[jobId]["SubmissionHost"] = job.SubmissionHost
                        self.jobDict[jobId]["SubmissionClientName"] = job.SubmissionClientName
                        self.jobDict[jobId]["OtherMessages"] = job.OtherMessages
                        self.jobDict[jobId]["VirtualMachine"] = job.VirtualMachine
                        self.jobDict[jobId]["UsedCPUType"] = job.UsedCPUType
                        self.jobDict[jobId]["UsedOSFamily"] = job.UsedOSFamily
                        self.jobDict[jobId]["UsedPlatform"] = job.UsedPlatform
                        self.jobDict[jobId]["Error"] = job.Error
                        self.jobDict[jobId]["RequestedWallTime"] = job.RequestedWallTime
                        self.jobDict[jobId]["RequestedTotalCPUTime"] = job.RequestedTotalCPUTime
                        self.jobDict[jobId]["ExecutionNode"] = job.ExecutionNode
                        self.jobDict[jobId]["UsedWallTime"] = job.UsedWallTime
                        self.jobDict[jobId]["UsedTotalCPUTime"] = job.UsedTotalCPUTime
                        self.jobDict[jobId]["UsedApplicationEnvironment"] = job.UsedApplicationEnvironment
                        self.jobDict[jobId]["LocalSubmissionTime"] = job.LocalSubmissionTime
                        self.jobDict[jobId]["SubmissionTime"] = job.SubmissionTime
                        self.jobDict[jobId]["ComputingManagerSubmissionTime"] = job.ComputingManagerSubmissionTime
                        self.jobDict[jobId]["StartTime"] = job.StartTime
                        self.jobDict[jobId]["ComputingManagerEndTime"] = job.ComputingManagerEndTime
                        self.jobDict[jobId]["EndTime"] = job.EndTime
                        self.jobDict[jobId]["WorkingAreaEraseTime"] = job.WorkingAreaEraseTime
                        self.jobDict[jobId]["ProxyExpirationTime"] = job.ProxyExpirationTime
                        self.jobDict[jobId]["CreationTime"] = job.CreationTime
                        self.jobDict[jobId]["Validity"] = job.Validity
                    except:
                        pass
                                      
    def sortKeysBy(self, byField=""):
        """
        Sort job dictionary by field specified by the byField parameter.
        """
        keys = self.jobDict.keys()
        if byField == "":
            keys.sort(lambda x, y: cmp(x, y))
        else:
            try:
                keys.sort(lambda x, y: cmp(self.jobDict[x][byField], self.jobDict[y][byField]) )
            except:
                keys.sort(lambda x, y: cmp(x, y))
        return keys
            
    def printJobs(self):
        """
        Print list of jobs managed by this class.
        """
        for jobId in self.jobDict.keys():
            print jobId

    def printStatus(self):
        """
        Print status of jobs.
        """
        jobmaster = arc.JobSupervisor(self.userConfig, [], [], self.jobListFilename)        
        jobcontrollers = jobmaster.GetJobControllers();
        
        jobStatus = []
        
        for job in jobcontrollers:
          job.Stat(jobStatus, True)
        
    debugLevel = property(getDebugLevel, setDebugLevel)
    proxyFilename = property(getProxyFilename, setProxyFilename)
    logStream = property(getLogStream, setLogStream)
    logFilename = property(getLogFilename, setLogFilename)
