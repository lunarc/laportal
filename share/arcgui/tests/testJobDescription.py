#!/bin/env python

import arc, os, sys

sys.path.append("..")

from Clients import *

xrslDescription = """
&(executable="/bin/sh")
(arguments="run.sh")
(inputFiles=("run.sh" ""))
(outputFiles=("result.txt" ""))
(runTimeEnvironment>="ENV/PYTHON-2.5.2")
(stdout="stdout.txt")
(stderr="stderr.txt")
(wallTime="5 minutes")
"""

#job2 = ManagedJobDescription()
#job2.Parse(xrslDescription)
#job2.Print(True)

job = ManagedJobDescription()
job.Application.Executable.Name = "/bin/sh"
job.Application.Output = "stdout.txt"
job.Resources.TotalWallTime = arc.ScalableTimeInt(3600)
job.addArgument("run.sh")
job.addInputFile("run.sh")
job.addOutputFile("result.txt")
job.addRuntimeEnvironment("ENV/PYTHON",">=", "2.4")
job.Print(True)
print job.UnParse("xrsl")
#print job2.UnParse("xrsl")

