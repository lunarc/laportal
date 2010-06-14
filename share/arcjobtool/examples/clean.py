#!/usr/bin/python

import arc, sys;

# User configuration file.
# Initialise a default user configuration.
usercfg = arc.UserConfig("");

# List of job ids to process.
jobids = sys.argv[1:];

# List of clusters to process.
clusters = [];

# Job list containing active jobs.
joblist = "myjoblist";

# Process only jobs with the following status codes.
# If list is empty all jobs will be processed.
status = [];

# Force cleaning.
force = False;

# Logging...
logger = arc.Logger(arc.Logger_getRootLogger(), "arcstat.py");
logcout = arc.LogStream(sys.stdout);
arc.Logger_getRootLogger().addDestination(logcout);
arc.Logger_getRootLogger().setThreshold(arc.DEBUG);


jobmaster = arc.JobSupervisor(usercfg, jobids, clusters, joblist);
jobcontrollers = jobmaster.GetJobControllers();

for job in jobcontrollers:
  job.Clean(status, force);

