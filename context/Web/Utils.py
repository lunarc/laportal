import os
import string
import sys

class logger:
	def __init__(self):
		self.loggin = True
		self.context = "LAP"
		self.function = ""
		
	def doMessage(self, message):
		if self.loggin:
			print self.context+": "+self.function+"() "+message

	def msg(self, context, function="", message=""):
		self.context = context
		self.function = function
		self.doMessage(message)
		
	def setLoggin(self, flag):
		self.loggin = flag


log = logger()

def simpleExec(commandLine):
	print "Executing ", commandLine
	stdinFile, stdoutFile, stderrFile = os.popen3(commandLine)
	#stdoutFile = os.popen(commandLine)
	stdout = stdoutFile.readlines()
	stdoutFile.close()
	stderr = stderrFile.readlines()
	stderrFile.close()
	stdinFile.close()

	result = []
	
	print "--->"
	for line in stdout:
		print string.strip(line)
		result.append(string.strip(line))

	for line in stderr:
		print string.strip(line)
		result.append(string.strip(line))
	print "<---"
	return result
