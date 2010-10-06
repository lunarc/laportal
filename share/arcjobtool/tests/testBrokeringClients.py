#!/bin/env python

import arc, sys, os;

sys.path.append("..")

from Clients import *

print "--- Setting up ArcClient ---"

arcClient = ArcClient()
arcClient.debugLevel = arc.ERROR

print "--- Create a job description ---"

#xrslDescription = """
#&(executable="/bin/sh")
#(arguments="run.sh")
#(inputFiles=("run.sh" ""))
#(stdout="stdout.txt")
#(stderr="stderr.txt")
#"""
#
#job = arc.JobDescription();
#if not job.Parse(xrslDescription):
#    print "Could not parse job description"
#    sys.exit(-1)
    
#job.TotalWallTime = arc.Period("5",arc.PeriodMinutes)
#job.Print(True)
    
job = ManagedJobDescription()
job.Application.Executable.Name = "/bin/sh"
job.Application.Output = "stdout.txt"
job.Application.Error = "stderr.txt"
job.Resources.TotalWallTime = arc.ScalableTimeInt(300)
job.addArgument("run.sh")
job.addInputFile("run.sh")
job.addOutputFile("result.txt")
job.addRuntimeEnvironment("ENV/PYTHON","<=", "2.5")
job.Print(True)

print "--- Job description in XRSL ---"

print job.UnParse("xrsl")
   
print "--- Find suitable targets ---"

arcClient.findTargets()

print "--- Found targets ---"

for target in arcClient.targets:
    print target.ServiceName

print "--- Find best target ---"

target = arcClient.findBestTarget(job)

print "--- Chosen target ---"

print target.ServiceName

#print "--- Submitting jobs ---"

#submitter = target.GetSubmitter(userConfig)

#for i in range(1):
#    url = submitter.Submit(job, target)
#    print url.fullstr()
