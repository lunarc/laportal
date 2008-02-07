#!/bin/env python

#
# LAP System module
#
# Copyright (C) 2006-2008 Jonas Lindemann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""LAP system module."""

from Lap.Log import *

import os, commands, string

def getstatusoutput(cmd, env=None, startDir=""):
	
	variableDefs = ""
	
	if env!=None:
		for variableName in env.keys():
			variableDefs = variableDefs + "%s=%s " % (variableName, env[variableName])
	
	execCmd = variableDefs + cmd
	
	if startDir == "":
		resultVal, result = commands.getstatusoutput(execCmd)
	else:
		resultVal, result = commands.getstatusoutput('cd "%s";set;%s' % (startDir, execCmd))
	
	resultLines = result.split('\n')
	
	lapInfo("Executing: %s, result = %d" % (cmd, resultVal))
	#lapDebug(variableDefs)
	
	if len(resultLines)<200:
		i = 0
		for line in resultLines:
			lapDebug("\t"+str(i)+": "+line.strip())
			i = i + 1
	
	return resultVal, resultLines

def popen(cmd, env=None):
	
	variableDefs = ""
	
	if env!=None:
		for variableName in env.keys():
			variableDefs = variableDefs + "%s=%s " % (variableName, env[variableName])
	
	execCmd = variableDefs + cmd
	
	f = os.popen(execCmd)
	
	lapInfo("Executing: %s" % (cmd))

	return f

if __name__ == "__main__":
	
	resultVal, result = getstatusoutput("/bin/ls")
	resultVal
	print result
	
	
