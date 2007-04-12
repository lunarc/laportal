#!/usr/bin/python

# You can pass several parameters on the command line
# (more info by running this with option --help)
# or you can modify the default values here
# (more info in WebKit.Launch):

import os, sys, logging

currDir = os.getcwd()
sys.path.insert(0, os.path.join(currDir, "LapConfig"))

import LapSite

lapContext  = LapSite.Application["ContextName"]
webwarePath = LapSite.Dirs["WebWareDir"]
appWorkPath = LapSite.Dirs["AppWorkDir"]
extraPath   = LapSite.Dirs["DependsDir"]
contextPath = os.path.join(appWorkPath, lapContext)

# Setup arclib

arclibPath = os.path.join(LapSite.Dirs["NorduGridDir"], "lib")
arclibPythonPath = os.path.join(LapSite.Dirs["NorduGridDir"], "lib/python2.3/site-packages")

sys.path.append(arclibPythonPath)

libraryDirs = [contextPath, extraPath]
runProfile = 0
logFile = LapSite.Logging["WebWareLogFile"]
pidFile = LapSite.System["ServerPIDFile"]
user = LapSite.System["ServerUser"]
group = LapSite.System["ServerGroup"]

sys.path.insert(0, webwarePath)

from WebKit import Launch

Launch.workDir = appWorkPath
Launch.webwareDir = webwarePath
Launch.libraryDirs = libraryDirs
Launch.runProfile = runProfile
Launch.logFile = logFile
Launch.pidFile = pidFile
Launch.user = user
Launch.group = group

# Setup logging

logger = logging.getLogger('lap')
hdlr = logging.FileHandler(LapSite.Logging["LogFile"])
formatter = logging.Formatter('%(asctime)s %(levelname)s\t: %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)

if LapSite.Logging.has_key("LogLevel"):
        if LapSite.Logging["LogLevel"] == "DEBUG":
                logger.setLevel(logging.DEBUG)
        elif LapSite.Logging["LogLevel"] == "WARNING":
                logger.setLevel(logging.WARNING)
        elif LapSite.Logging["LogLevel"] == "INFO":
                logger.setLevel(logging.INFO)
        else:
                logger.setLevel(logging.WARNING)
else:
        logger.setLevel(logging.WARNING)


if __name__ == '__main__':

        logger.info("-----------------------------------")
        logger.info("Lunarc Application Portal starting ")
        logger.info("-----------------------------------")

	Launch.main()

        logger.info("-----------------------------------")
        logger.info("Lunarc Application Portal shutdown ")
        logger.info("-----------------------------------")
