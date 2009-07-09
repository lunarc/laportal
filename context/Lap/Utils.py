import os, string, sys, re

def listFilesAndDirectories(dirPath):
	"""List files and directories in specified path.
	Return a list of files and a list of directories."""
	
	fileList = []
	dirList = []
	
	for entry in os.listdir(dirPath):
		atime = os.path.getatime(os.path.join(dirPath,entry))
		mtime = os.path.getmtime(os.path.join(dirPath,entry))
		fsize = os.path.getsize(os.path.join(dirPath,entry))
		if os.path.isdir(os.path.join(dirPath,entry)):
			dirList.append((entry, atime, mtime, fsize, os.path.join(dirPath,entry)))
		else:
			fileList.append((entry, atime, mtime, fsize, os.path.join(dirPath,entry)))
			
	return fileList, dirList

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
