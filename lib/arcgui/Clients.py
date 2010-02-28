#!/usr/bin/python

#
# Clients - Wrapper class for the libarclient library.
#

"""
Class wrappers for grid client libraries.
"""

import arc, sys, os, getpass

import ConfigParser

def zeroString(string):
    # find the header size with a dummy string
    temp = "finding offset"
    header = ctypes.string_at(id(temp), sys.getsizeof(temp)).find(temp)
 
    location = id(string) + header
    size     = sys.getsizeof(string) - header
 
    #memset =  ctypes.cdll.msvcrt.memset
    # For Linux, use the following. Change the 6 to whatever it is on your computer.
    memset =  ctypes.CDLL("libc.so.6").memset
 
    self.logInfoMsg("Clearing 0x%08x size %i bytes" % (location, size))
 
    memset(location, 0, size)
    
class ArcGuiConfig(object):
    def __init__(self, userConfig, arcClient):
        self.userConfig = userConfig
        self.arcClient = arcClient
        self.__initDefaultProperties()        
        self.__filename = "arcgui.conf"
        
    def addDefaultService(self, serviceName):
        self.defaultServices.append(serviceName)
        
    def clearDefaultServices(self):
        self.defaultServices = []
        
    def addRejectedService(self, serviceName):
        self.rejectedServices.append(serviceName)
        
    def clearRejectedServices(self):
        self.rejectedServices = []

    def write(self):
        parser = ConfigParser.RawConfigParser()
        if not parser.has_section("common"):
            parser.add_section("common")

        if len(self.defaultServices)>0:
            parser.set("common", "defaultservices", " ".join(self.defaultServices))
            
        if len(self.rejectedServices)>0:
            parser.set("common", "rejectedservices", " ".join(self.rejectedServices))
            
        if self.brokerName!="":
            parser.set("common", "brokername", self.brokerName)
            
            if self.brokerArguments!="":
                parser.set("common", "brokerarguments", self.brokerArguments)
                                
        parser.set("common", "timeout", str(self.timeout))
        parser.set("common", "proxypath", self.proxyPath)
        parser.set("common", "keypath", self.keyPath)
        parser.set("common", "certificatepath", self.certificatePath)
        parser.set("common", "cacertificatesdirectory", self.cacertificatesDirectory)
        
        parser.add_section("arcgui")
        parser.set("arcgui", "automaticdownload", self.automaticDownload)
        parser.set("arcgui", "automaticdownloadinterval", self.automaticDownloadInterval)
        parser.set("arcgui", "automaticupdate", self.automaticUpdate)
        parser.set("arcgui", "automaticupdateinterval", self.automaticUpdateInterval)
        
        configFile = open(self.__filename, "w")
        parser.write(configFile)
        configFile.close()
        
    def __initDefaultProperties(self):
        
        # ARC properties
        
        self.defaultServices = []
        self.rejectedServices = []
        self.__brokerName = "Random"
        self.brokerArguments = ""
        self.timeout = "50"
        self.proxyPath = ""
        self.keyPath = ""
        self.certificatePath = ""
        self.cacertificatesDirectory = ""
        
        uid = os.getuid()

        if self.certificatePath == "":
            self.certificatePath = os.path.expanduser("~/.globus/usercert.pem")
            self.userConfig.CertificatePath(self.certificatePath)
            
        if self.keyPath == "":
            self.keyPath = os.path.expanduser("~/.globus/userkey.pem")
            self.userConfig.KeyPath(self.keyPath)
            
        if self.cacertificatesDirectory == "":
            self.cacertificatesDirectory = "/etc/grid-security/certificates"
            self.userConfig.CACertificatesDirectory(self.cacertificatesDirectory)
        
        if self.proxyPath == "":
            self.proxyPath = "/tmp/x509up_u%d" % uid
            self.userConfig.ProxyPath(self.proxyPath)
            
        # ArcClient properties
        
        if self.arcClient!=None:
            self.arcClient.brokerName = self.brokerName
        
        # ARCGUI properties
        
        self.automaticDownload = False
        self.automaticDownloadInterval = 120000
        
        self.automaticUpdate = True
        self.automaticUpdateInterval = 60000
        
        self.showSplash = True
        
    def update(self):
        self.write()
        self.read()
        
    def create(self):
        self.__initDefaultProperties()
        self.write()

    def read(self):
        
        self.userConfig.LoadConfigurationFile(self.__filename, True)
        
        self.__initDefaultProperties()
        
        # Load what we can from UserConfig.

        self.timeout = self.userConfig.Timeout()
        self.proxyPath = str(self.userConfig.ProxyPath())
        #self.keyPath = str(self.userConfig.KeyPath())
        #self.certificatePath = str(self.userConfig.CertificatePath())
        self.cacertificatesDirectory = str(self.userConfig.CACertificatesDirectory())
                    
        # Due to API problems we can't get everything from UserConfig. Here we
        # parse the ini-file to get the missing pieces.
        
        parser = ConfigParser.RawConfigParser()
        parser.read(self.__filename)
        
        if parser.has_section("common"):
            if parser.has_option("common", "defaultservices"):
                defaultServicesText = parser.get("common", "defaultservices")
                self.defaultServices = defaultServicesText.strip().split()
            if parser.has_option("common", "rejectedservices"):
                rejectedServicesText = parser.get("common", "rejectedservices")
                self.rejectedServices = rejectedServicesText.strip().split()
                
            if parser.has_option("common", "brokername"):
                self.brokerName = parser.get("common", "brokername")
                
            if parser.has_option("common", "certificatepath"):
                self.certificatePath = parser.get("common", "certificatepath")
            if parser.has_option("common", "keypath"):
                self.keyPath = parser.get("common", "keypath")
                
        if parser.has_section("arcgui"):
            if parser.has_option("arcgui", "automaticdownload"):
                self.automaticDownload = parser.getboolean("arcgui", "automaticdownload")
            if parser.has_option("arcgui", "automaticdownloadinterval"):
                self.automaticDownloadInterval = int(parser.get("arcgui", "automaticdownloadinterval"))
            if parser.has_option("arcgui", "automaticupdate"):
                self.automaticUpdate = parser.getboolean("arcgui", "automaticupdate")
            if parser.has_option("arcgui", "automaticupdateinterval"):
                self.automaticUpdateInterval = int(parser.get("arcgui", "automaticupdateinterval"))
                
        uid = os.getuid()

        if self.certificatePath == "":
            self.certificatePath = os.path.expanduser("~/.globus/usercert.pem")
            
        if self.keyPath == "":
            self.keyPath = os.path.expanduser("~/.globus/userkey.pem")
            
        if self.cacertificatesDirectory == "":
            self.cacertificatesDirectory = "/etc/grid-security/certificates"
        
        if self.proxyPath == "":
            self.proxyPath = "/tmp/x509up_u%d" % uid
                       
        self.userConfig.CertificatePath(self.certificatePath)
        self.userConfig.KeyPath(self.keyPath)
        self.userConfig.CACertificatesDirectory(self.cacertificatesDirectory)
        self.userConfig.ProxyPath(self.proxyPath)                
        
        #for section in parser.sections():
        #    print section
        #    for option in parser.options(section):
        #        print " ", option, "=", parser.get(section, option)
                
    def setFilename(self, filename):
        self.__filename = filename
                
    def getFilename(self):
        return self.__filename
    
    def getBrokerName(self):
        return self.__brokerName
        
    def setBrokerName(self, brokerName):
        self.userConfig.Broker(brokerName)
        if self.arcClient!=None:
            self.arcClient.brokerName = brokerName
        self.__brokerName = brokerName
    
    brokerName = property(getBrokerName, setBrokerName)

    filename = property(getFilename, setFilename)


class UserAuthentication(object):
    """
    Class implementing different user authentication mechanism.
    """
    def __init__(self, userConfig):
        """
        Class constructor
        """
        
        self.userConfig = userConfig
        
        self.certificatePath = self.userConfig.CertificatePath()
        self.keyPath = self.userConfig.KeyPath()
        self.caDir = self.userConfig.CACertificatePath()
        self.proxyPath = self.userConfig.ProxyPath()
        
        self.period = "12"
        self.keybits = 1024
        self.prompt = ""
        self.proxyType = "gsi2"
        self.errorMessage = ""
        
        self.__logger = arc.Logger(arc.Logger_getRootLogger(), "UserAuth")                

    def logMsg(self, level, msg):
        self.__logger.msg(level, msg)
        
    def logInfoMsg(self, msg):
        self.logMsg(arc.INFO, msg)
    
    def logDebugMsg(self, msg):
        self.logMsg(arc.DEBUG, msg)

    def logErrorMsg(self, msg):
        self.logMsg(arc.ERROR, msg)        

    def onPassphrasePrompt(self, prompt=""):
        """
        Virtual method for querying the user for a password. Should be overidden
        by derived classes.
        """
        if prompt == "":
            return getpass.getpass("Passphrase:")
        else:
            return getpass.getpass(prompt)
        
    def createLocalProxy(self, proxyType = "gsi2"):
        """
        Create a local proxy certificate
        """
        
        if self.proxyPath == "":
            self.proxyPath = "/tmp/x509up_u%d" % os.getuid()
        
        # --- Load user certificate and key ---
        
        self.logInfoMsg("Load user certificate and key.")
        
        passphrase = self.onPassphrasePrompt(self.prompt)
        if passphrase == "":
            self.errorMessage = ""
            return False
                
        signer = arc.Credential(self.certificatePath, self.keyPath, self.caDir, "", str(passphrase))
        
        #zeroString(passphrase)
        del passphrase
        
        # --- Setup proxy parameters ---
        
        start = arc.Time()
        arcPeriod = arc.Period(self.period, arc.PeriodHours)
        policy = ""
        
        # --- Create proxy certificate request ---
        
        self.logInfoMsg("Create proxy certificate request.")
        
        credRequest = arc.Credential(start, arcPeriod, self.keybits, "rfc", "inheritAll", policy, -1)
        generateRequestOk, requestString = credRequest.GenerateRequest()
        
        if not generateRequestOk:
            self.errorMessage = "Could not generate proxy certificate request."
            return False
        
        outputPrivateKeyOk, privateKey = credRequest.OutputPrivatekey()

        if not outputPrivateKeyOk:
            self.errorMessage = "Could not generate private key."
            return False
        
        outputCertificateOk, signingCert = signer.OutputCertificate()
        
        if not outputCertificateOk:
            self.errorMessage = "Could not get user certificate."
            return False
        
        outputCertificateChainOk, signingCertChain = signer.OutputCertificateChain()
        
        if not outputCertificateOk:
            self.errorMessage = "Could not get certificate chain."
            return False

        # --- Set proxy type ---
        
        if self.proxyType == "rfc":
            credRequest.SetProxyPolicy("rfc", "inheritAll", "", -1)
        else:
            credRequest.SetProxyPolicy("gsi2", "", "", -1)
        
        # --- Sign request with user certificate ---
        
        self.logInfoMsg("Sign request with user certificate.")
        
        signRequestOk, proxyCert = signer.SignRequest(credRequest)
        
        if not signRequestOk:
            self.errorMessage = "Failed to sign proxy request."
            return False
        
        
        # --- Create proxy certificate file ---
        
        fullProxyCert = proxyCert + privateKey + signingCert + signingCertChain
        
        proxyCertFile = open(self.proxyPath, "w")
        proxyCertFile.write(fullProxyCert)
        proxyCertFile.close()
        
        # --- Set the correct permissions on the file ---
        
        os.chmod(self.proxyPath, 0600)
        
        return True

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
        self.Application.Executable.Argument.append(argument)
    
    def addInputFile(self, name, url="", keepData = True, isExecutable = False, downloadToCache = False, threads = -1):
        """
        Add an input file, name, to the job description.
        """
        inputFile = arc.FileType()
        inputFile.Name = str(os.path.basename(name))
        inputFile.KeepData = False
        inputFile.IsExecutable = False
        inputFile.DownloadToCache = False
        inputFileSource = arc.DataSourceType()
        if url=="":
            fullPath = os.path.abspath(name)
            urlRepr = "file://"+fullPath
            inputFileSource.URI = arc.URL(str(urlRepr))
        else:
            inputFileSource.URI = arc.URL(url)
        inputFile.Source.append(inputFileSource)
        self.DataStaging.File.append(inputFile)
        
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
        outputFileTarget = arc.DataTargetType()
        outputFileTarget.URI = arc.URL(url)
        outputFileTarget.Threads = threads
        outputFileTarget.Mandatory = True
        outputFile.Target.append(outputFileTarget)
        self.DataStaging.File.append(outputFile)
        
    def clearOutputFiles(self):
        """
        Clear output files.
        """
        pass
    
    def addRuntimeEnvironment(self, name, relOp, version):
        """
        Add a runtime environment and version.
        """
        softReq = arc.SoftwareRequirement()
        software = arc.Software(name+"-"+version)
        
        arcRelOp = arc.Software.GREATERTHANOREQUAL
        
        if relOp == "<":
            arcRelOp = arc.Software.LESSTHAN
        elif relOp == "<=":
            arcRelOp = arc.Software.LESSTHANOREQUAL
        elif relOp == "==":
            arcRelOp = arc.Software.EQUAL
        elif relOp == ">=":
            arcRelOp = arc.Software.GREATERTHANOREQUAL
        elif relOp == ">":
            arcRelOp = arc.Software.GREATERTHAN
        
        self.Resources.RunTimeEnvironment.add(software, arcRelOp)
        
class ArcClient(object):
    def __init__(self, userConfig=None, logStream=None):
        """
        ArcClient class constructor
        
        Initialises properties and variables, sets up logging and
        loads job list.
        """
        
        # Setup ARC logging
        
        self.__logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient")                
        
        # Setup class properties
        
        self.__proxyFilename = ""
        self.jobListFilename = os.path.expanduser("~/.arc/jobs.xml")
        self.userConfigFilename = os.path.expanduser("~/.arc/arcgui.conf")
        self.downloadDir = "."
        
        # Setup user configuration
        
        self.logInfoMsg("Creating UserConfig.")
        if userConfig == None:
            self.userConfig = arc.UserConfig(self.userConfigFilename, self.jobListFilename, True)
        else:
            self.userConfig = userConfig
                       
        self.targets = []
        self.filteredTargets = []
        self.jobList = None
        self.jobDict = {}
        self.clusters = []
        self.__debugLevel = arc.VERBOSE
        self.__doFiltering = True
        self.updateProgress = None
        self.currentTarget = None
        self.__brokerName = "Random"
                
        #self.__logStream = logStream
        
        #if self.__logStream==None:
        #    self.__logStream = sys.stdout
        
        #logcout = arc.LogStream(self.__logStream)
        #arc.Logger_getRootLogger().removeDestinations()       
        #arc.Logger_getRootLogger().addDestination(logcout)
        #arc.Logger_getRootLogger().setThreshold(self.__debugLevel)
        
        # Setup ACC loader
        
        self.logInfoMsg("Create BrokerLoader.")
        
        self.__brokerLoader = arc.BrokerLoader()
        self.__broker = self.__brokerLoader.load(self.__brokerName, self.userConfig)
                
        self.logInfoMsg("Create TargetGenerator.")
        
        self.__targetGenerator = arc.TargetGenerator(self.userConfig);
        
        # Initialise joblist
        
        self.logInfoMsg("Initialise job list.")
        
        self.__loadJobs()
        
    def logMsg(self, level, msg):
        self.__logger.msg(level, msg)
        
    def logInfoMsg(self, msg):
        self.logMsg(arc.INFO, msg)
    
    def logDebugMsg(self, msg):
        self.logMsg(arc.DEBUG, msg)

    def logErrorMsg(self, msg):
        self.logMsg(arc.ERROR, msg)        
        
    def setLogStream(self, stream):
        """
        Assigns the logstream to instance.
        """
        self.__logStream = stream
        logcout = arc.LogStream(stream);
        arc.Logger_getRootLogger().removeDestinations()
        arc.Logger_getRootLogger().addDestination(logcout)

    def getLogStream(self,):
        """
        Return current log stream.
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
        Set proxy filename.
        """
        self.__proxyFilename = filename
        
    def getProxyFilename(self):
        """
        Return proxy filename
        """
        return self.__proxyFilename
    
    def saveConfiguration(self):
        """
        Save current configuration.
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
                
    def loadJobList(self):
        """
        Load job list from XML file.
        """
        self.__loadJobs()
                
    def hasValidProxy(self):
        """
        Return status of proxy.
        """
        return self.userConfig.CheckProxy()

    def findTargets(self):
        """
        Find possible targets by querying information system.
        """
        
        self.doProgress("Finding suitable targets.")
        
        self.targets = None
        self.__targetGenerator = arc.TargetGenerator(self.userConfig);
        self.__targetGenerator.GetTargets(0, 1);
        self.targets = self.__targetGenerator.ModifyFoundTargets()
        
    def loadBroker(self, brokerName="Random"):
        """
        Wrapper function for encapsulating ARC1 loading of
        of a broker instance.
        """
        
        return self.__loader.load(brokerName, self.userConfig)
        
    def filterTargets(self, job):
        self.findBestTarget(job)
        
    def findBestTarget(self, job):
        """
        Return a filtered list of suitable targets based on the
        RandomBroker component.
        """
        self.doProgress("Prefiltering targets.")

        self.__broker = self.__brokerLoader.load(self.__brokerName, self.userConfig)
        self.__broker.PreFilterTargets(self.targets, job)

        self.currentTarget = self.__broker.GetBestTarget()
        
        return self.currentTarget
        
    def submit_old(self, job):
        """
        Submit job to grid. Requires that a list of filtered targets
        exists.
        """
        self.doProgress("Submitting job.")
        
        if self.currentTarget==None:
            return None
        
        submitter = self.currentTarget.GetSubmitter(self.userConfig)
        jobURL = submitter.Submit(job, self.currentTarget)
        self.logInfoMsg("Submitted: " + jobURL.fullstr())
        
        if jobURL!=None:
            self.doProgress("Updating job file.")
            self.__loadJobs()
            return jobURL
        else:
            return jobURL
        
    def submit(self, job):
        """
        Submit job to grid. Requires that a list of filtered targets
        exists.
        """
        self.doProgress("Submitting job.")
        
        if self.currentTarget==None:
            return None
        
        submitter = self.currentTarget.GetSubmitter(self.userConfig)
        jobURL = submitter.Submit(job, self.currentTarget)
        self.logInfoMsg("Submitted: " + jobURL.fullstr())
        
        if jobURL!=None:
            self.doProgress("Updating job file.")
            self.__loadJobs()
            return jobURL
        else:
            return jobURL

    def submitJobList(self, jobList):
        """
        Submit job list to grid. Requires a
        """
        self.doProgress("Submitting job.")

        resultList = [None]*len(jobList)

        if self.currentTarget=="":
            return resultList
        
        i = 0
        
        self.__broker = self.__brokerLoader.load(self.__brokerName, self.userConfig)
        
        for job in jobList:

            self.__broker.PreFilterTargets(self.targets, job)
            
            jobURL = None

            while True:
                bestTarget = self.__broker.GetBestTarget()
                if bestTarget!=None:
                    submitter = bestTarget.GetSubmitter(self.userConfig)
                    jobURL = submitter.Submit(job, bestTarget)
                    if jobURL!=None:
                        break

                    resultList[i] = jobURL
                else:
                    break
            
            if jobURL!=None:    
                self.doProgress("Updating job file.")
                self.__loadJobs()
                
            resultList[i] = jobURL
            i += 1
            
        return resultList
                        
    def get(self, jobIds = [], status = ["FINISHED", "FAILED"], keep=False):
        """
        Download results from jobs.
        """        
        self.doProgress("Retrieving job controllers.")
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds);
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
        
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds);
        jobControllers = jobSupervisor.GetJobControllers();
        
        for controller in jobControllers:
            controller.Kill(status, force);
        
        self.__loadJobs()
        
    def clean(self, jobIds = [], status = [], force = False):
        """
        Clean running jobs.
        """
        jobSupervisor = arc.JobSupervisor(self.userConfig, jobIds);
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
        
        """
        std::string Flavour;
        URL JobID;
        URL Cluster;
        // Optional information (ACCs fills if they need it)
        URL SubmissionEndpoint;
        URL InfoEndpoint;
        URL ISB;
        URL OSB;
        // ACC implementation dependent information
        URL AuxURL;
        std::string AuxInfo;
    
        // Information retrieved from the information system
        std::string Name;
        std::string Type;
        URL IDFromEndpoint;
        std::string LocalIDFromManager;
        std::string JobDescription;
        JobState State;
        std::string RestartState;
        std::map<std::string, std::string> AuxStates; //for all state models
        std::map<std::string, std::string> RestartStates; //for all state models
        int ExitCode;
        std::string ComputingManagerExitCode;
        std::list<std::string> Error;
        int WaitingPosition;
        std::string UserDomain;
        std::string Owner;
        std::string LocalOwner;
        Period RequestedTotalWallTime;
        Period RequestedTotalCPUTime;
        int RequestedMainMemory; // Deprecated??
        int RequestedSlots;
        std::list<std::string> RequestedApplicationEnvironment;
        std::string StdIn;
        std::string StdOut;
        std::string StdErr;
        std::string LogDir;
        std::list<std::string> ExecutionNode;
        std::string ExecutionCE; // Deprecated??
        std::string Queue;
        Period UsedTotalWallTime;
        Period UsedTotalCPUTime;
        int UsedMainMemory;
        std::list<std::string> UsedApplicationEnvironment;
        int UsedSlots;
        Time LocalSubmissionTime;
        Time SubmissionTime;
        Time ComputingManagerSubmissionTime;
        Time StartTime;
        Time ComputingManagerEndTime;
        Time EndTime;
        Time WorkingAreaEraseTime;
        Time ProxyExpirationTime;
        std::string SubmissionHost;
        std::string SubmissionClientName;
        Time CreationTime;
        Period Validity;
        std::list<std::string> OtherMessages;
        //Associations
        URL JobManagementEndpoint;
        URL DataStagingEndpoint;
        std::list<std::string> ActivityOldId;
        //ExecutionEnvironment (condensed)
        bool VirtualMachine;
        std::string UsedCPUType;
        std::string UsedOSFamily;
        std::string UsedPlatform;
        """ 
        
        
        self.doProgress("Creating job supervisor.")
        
        self.logInfoMsg("Creating JobSupervisor")
        jobSupervisor = arc.JobSupervisor(self.userConfig, [])
        self.logInfoMsg("Retrieving job controllers.")
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
                    self.jobDict[jobId]["State"] = jobState()
                    self.jobDict[jobId]["Name"] = job.Name
                    
                    if len(job.Error)>0:
                        self.jobDict[jobId]["Error"] = str(job.Error[0])
                    else:
                        self.jobDict[jobId]["Error"] = ""
                    
                    self.jobDict[jobId]["Cluster"] = job.Cluster.fullstr()
                    self.jobDict[jobId]["SubmissionEndpoint"] = job.SubmissionEndpoint.fullstr()
                    self.jobDict[jobId]["InfoEndpoint"] = job.InfoEndpoint.fullstr()
                    self.jobDict[jobId]["Type"] = job.Type
                    self.jobDict[jobId]["JobDescription"] = job.JobDescription
                    self.jobDict[jobId]["ExitCode"] =   job.ExitCode
                    self.jobDict[jobId]["UserDomain"] = job.UserDomain
                    self.jobDict[jobId]["LocalIdFromManager"] = job.LocalIDFromManager
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
                    self.jobDict[jobId]["RequestedTotalWallTime"] = job.RequestedTotalWallTime
                    self.jobDict[jobId]["RequestedTotalCPUTime"] = job.RequestedTotalCPUTime
                    self.jobDict[jobId]["ExecutionNode"] = job.ExecutionNode
                    self.jobDict[jobId]["UsedTotalWallTime"] = job.UsedTotalWallTime
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
          
    def getBrokerName(self):
        return self.__brokerName
        
    def setBrokerName(self, brokerName):
        self.userConfig.Broker(brokerName)
        self.__brokerName = brokerName
        
    def setTimeout(self, timeout):
        self.userConfig.Timeout(timeout)
        
    def getTimeout(self):
        return self.userConfig.Timeout()
        
    debugLevel = property(getDebugLevel, setDebugLevel)
    proxyFilename = property(getProxyFilename, setProxyFilename)
    logStream = property(getLogStream, setLogStream)
    brokerName = property(getBrokerName, setBrokerName)
    timeout = property(getTimeout, setTimeout)
    
