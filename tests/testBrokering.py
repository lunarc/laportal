#!/bin/env python

import arc, sys, os;

sys.path.append("..")

from Clients import *

print "--- Setup logging ---"

logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient");
logcout = arc.LogStream(sys.stdout);
arc.Logger_getRootLogger().addDestination(logcout);
arc.Logger_getRootLogger().setThreshold(arc.ERROR);

print "--- Load user configuration ---"

userConfig = arc.UserConfig("/home/jonas/.arc/client.conf", "/home/jonas/.arc/jobs.xml")
userConfig.InitializeCredentials()

print "--- Create a job description ---"

job = ManagedJobDescription()
job.Application.Executable.Name = "/bin/sh"
job.Application.Output = "stdout.txt"
job.Application.Error = "stderr.txt"
job.Resources.TotalWallTime = arc.ScalableTimeInt(300)
job.addArgument("run.sh")
job.addInputFile("run.sh")
job.addOutputFile("result.txt")
job.addRuntimeEnvironment("ENV/PYTHON","<","2.5")
job.Print(True)

print "--- Job description in XRSL ---"

print job.UnParse("xrsl")
   
print "--- Find suitable targets ---"

targetGenerator = arc.TargetGenerator(userConfig);
targetGenerator.GetTargets(0, 1);
foundTargets = targetGenerator.ModifyFoundTargets()

print "--- Found targets ---"

for target in foundTargets:
    print target.ServiceName

print "--- Loading broker ---"

brokerLoader = arc.BrokerLoader()
broker = brokerLoader.load("Random", userConfig)
broker.PreFilterTargets(foundTargets, job)

print "--- Prefiltered targets ---"

for target in foundTargets:
    print target.ServiceName

print "--- Chosen target ---"

target = broker.GetBestTarget()
print target.ServiceName

print "--- Submitting jobs ---"

submitter = target.GetSubmitter(userConfig)

for i in range(1):
    url = submitter.Submit(job, target)
    print url.fullstr()
