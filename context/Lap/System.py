#!/bin/env python

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
		resultVal, result = commands.getstatusoutput('cd "%s";%s' % (startDir, execCmd))
	
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
	
	