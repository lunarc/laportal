#!/bin/env python

import arc, sys, os;

userConfig = arc.UserConfig("~/.arc/client.xml", "~/.arc/jobs.xml")
userConfig.InitializeCredentials()

logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient");
logcout = arc.LogStream(sys.stdout);
arc.Logger_getRootLogger().addDestination(logcout);
arc.Logger_getRootLogger().setThreshold(arc.DEBUG);

# Define a job

# Create job description
#        (inputFiles=("run.sh" ""))


xrslDescription = """
&(executable="/bin/sh")
(arguments="run.sh")
(inputFiles=("run.sh" ""))
(stdout="stdout.txt")
(stderr="stderr.txt")
"""

job = arc.JobDescription();
if not job.Parse(xrslDescription):
    print "Could not parse job description"
    sys.exit(-1)
    
job.TotalWallTime = arc.Period("5",arc.PeriodMinutes)
job.Print(True)

#sys.exit(0)

# Find possible targets

targetGenerator = arc.TargetGenerator(userConfig, [], []);
targetGenerator.GetTargets(0, 1);
foundTargets = targetGenerator.ModifyFoundTargets()

print "--- Found targets ---"

for target in foundTargets:
    print target.ServiceName

# Load broker and do brokering

loaderConfig = arc.Config(arc.NS())
arc.ACCConfig().MakeConfig(loaderConfig)

loader = arc.ACCLoader(loaderConfig)
chosenBroker = loader.loadBroker("RandomBroker", userConfig)   
chosenBroker.PreFilterTargets(foundTargets, job)

print "--- Prefiltered targets ---"

for target in foundTargets:
    print target.ServiceName

filteredTargets = []

target = chosenBroker.GetBestTarget()
while not target==None:
    target = chosenBroker.GetBestTarget()
    if target!=None:
        filteredTargets.append(target)

print "--- Filtered targets ---"        
for target in filteredTargets:
    print target.ServiceName
    
