#!/usr/bin/python

import arc

import sys
sys.path.append("..")

from Clients import ArcClient
            
if __name__ == "__main__":
       
    xrslDescription = """
    &(executable="/bin/sh")
    (arguments="run.sh")
    (inputFiles=("run.sh" "")("main.py" ""))
    (stdout="stdout.txt")
    (stderr="stderr.txt")
    """
    
    job = arc.JobDescription();
    if not job.Parse(xrslDescription):
        print "Could not parse job description"
        sys.exit(-1)
        
    job.TotalWallTime = arc.Period("5",arc.PeriodMinutes)
    job.Print(True)
    
    client = ArcClient()
    client.debugLevel = arc.DEBUG
    client.findTargets()
    client.filterTargets(job)   
    client.submit(job)
