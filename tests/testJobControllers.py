#!/bin/env python

import arc, sys, os;

def readJobList(filename):
    
    jobDict = {}
    
    jobList = arc.Config(arc.NS())
    if os.path.exists(filename):
        jobList.ReadFromFile(filename)
        jobDict.clear()
        for j in jobList.Path("Job"):
            jobId = str(j.Get("JobID"))
            flavour = str(j.Get("Flavour"))
            
            if not jobDict.has_key(flavour):
                jobDict[flavour] = []
                
            jobDict[flavour].append(arc.URL(jobId))
            
    return jobList, jobDict
    

logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient");
logcout = arc.LogStream(sys.stdout);
arc.Logger_getRootLogger().addDestination(logcout);
arc.Logger_getRootLogger().setThreshold(arc.ERROR);

userConfigFilename = "/home/jonas/.arc/client.xml"
userJobListFilename = "/home/jonas/.arc/jobs.xml"

userConfig = arc.UserConfig(userConfigFilename, userJobListFilename)
userConfig.InitializeCredentials()

print "--- Read job list ---"

jobList, jobDict = readJobList(userJobListFilename)

print "--- Create job controllers ---"

controllers = []

controllerLoader = arc.JobControllerLoader()

for flavour in jobDict.keys():
    controller = controllerLoader.load(flavour, userConfig)
    controller.FillJobStore(jobDict[flavour], [], [])
    controllers.append(controller)
    
print "Found", len(controllers), "controllers."

if len(controllers)>0:
    
    for controller in controllers:
        
        controller.GetJobInformation()
        jobs = controller.GetJobs()
        
        for job in jobs:
            print "-------------------------------------------"
            print job.JobID.fullstr()
            print job.Flavour
            print job.State.GetGeneralState()
            if len(job.Error)>0:
                print "Error message:", len(job.Error)
                for i in range(len(job.Error)):
                    print job.Error[i]
