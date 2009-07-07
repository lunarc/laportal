#!/bin/env python

import arc, os, sys

from GridClients import *

xrslDescription = """
&(executable="/bin/sh")
(arguments="run.sh")
(inputFiles=("run.sh" ""))
(outputFiles=("result.txt" ""))
(runTimeEnvironment>="ENV/PYTHON-2.5.2")
(stdout="stdout.txt")
(stderr="stderr.txt")
"""

job = ManagedJobDescription()
job.Executable = "/bin/sh"
job.addArgument("run.sh")
job.addInputFile("run.sh")
job.addOutputFile("result.txt")
job.addRuntimeEnvironment("ENV/PYTHON","2.5.2")
job.TotalWallTime = arc.Period("5",arc.PeriodMinutes)
job.Output = "stdout.txt"
job.Print(True)

job2 = ManagedJobDescription()
job2.Parse(xrslDescription)
job2.Print(True)
