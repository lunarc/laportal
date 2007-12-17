"""WelcomePage module"""

import os, string

from Web.JsonPage import JsonPage
from HyperText.HTML import *

import LapSite

import simplejson

class JsonPluginList(JsonPage):
	"""Empty page displaying the default welcome text."""
	
	def __findJobPlugins(self):
		"""Parse the Plugin directory for job plugins. Returns
		a list containing available plugins."""
		
		pluginDir = LapSite.Dirs["PluginDir"]
		dirList = os.listdir(pluginDir)
		
		dirList.sort()
		
		pluginList = []
		
		for entry in dirList:
			fullPath = os.path.join(pluginDir, entry)
			if os.path.isdir(fullPath):
				infoFilename = os.path.join(fullPath,"Job.info")
				description = ""
				if os.path.isfile(infoFilename):
					infoFile = file(infoFilename)
					description = infoFile.readline().strip()
					infoFile.close()
					pluginList.append([entry, fullPath, entry, description])

		return pluginList	
	
	def onRenderJson(self):
		
		pluginList = self.__findJobPlugins()
		
		pluginTreeList = []
		
		i = 1000
		
		for plugin in pluginList:
			item = {}
			item["text"] = plugin[0]
			item["id"] = i
			item["leaf"] = True
			item["cls"] = "file"
			item["url"] = self.pageLoc()+"/Plugins/"+plugin[2]+"/CustomJobPage?createjob=0"			
			pluginTreeList.append(item)
			i+=1
		
		jsonString = simplejson.dumps(pluginTreeList)
		self.writeln(jsonString)
	

