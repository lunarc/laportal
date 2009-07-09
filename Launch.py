#!/usr/bin/python

# You can pass several parameters on the command line
# (more info by running this with option --help)
# or you can modify the default values here
# (more info in WebKit.Launch):

workDir = None
webwareDir = '/sw/pkg/Webware-1.0.1'
libraryDirs = ['/sw/lap/LapConfig', '/sw/lap/webkit_ext', '/sw/lap/webkit', '/sw/laportal/stable/context', '/sw/pkg/arc-trunk/lib64/python2.4/site-packages']
runProfile = 0
logFile = None
pidFile = None
user = None
group = None

import sys
sys.path.insert(0, webwareDir)
sys.path.insert(0, '/sw/lap/webkit_ext')

from WebKit import Launch

Launch.workDir = workDir
Launch.webwareDir = webwareDir
Launch.libraryDirs = libraryDirs
Launch.runProfile = runProfile
Launch.logFile = logFile
Launch.pidFile = pidFile
Launch.user = user
Launch.group = group

if __name__ == '__main__':
	Launch.main()
