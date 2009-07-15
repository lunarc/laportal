#!/usr/bin/python

import arc, sys, StringIO

from GridClients import ArcClient

#usercfg = arc.UserConfig("");
#joblist = "myjoblist";
#
#
## Logging...
#logger = arc.Logger(arc.Logger_getRootLogger(), "arcstat.py");
#logcout = arc.LogStream(sys.stdout);
#arc.Logger_getRootLogger().addDestination(logcout);
#arc.Logger_getRootLogger().setThreshold(arc.DEBUG);
#
#
#jobmaster = arc.JobSupervisor(usercfg, [sys.argv[1]], [], joblist);
##jobmaster = arc.JobSupervisor(usercfg, [], [], joblist);
#jobcontrollers = jobmaster.GetJobControllers();
#
#for job in jobcontrollers:
#  job.Stat([], True);

if __name__ == "__main__":
    
    client = ArcClient()
    client.debugLevel = arc.WARNING
    #client.printJobs()
    client.updateStatus()
    for jobId in client.jobs.keys():
        print jobId, client.jobs[jobId]["State"]
    #client.printJobs()
    
