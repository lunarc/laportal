from WebKit.Page import Page

import Web.Dialogs
import Web.Ui
import Lap.Session

import LapSite

import os, re

class VOListPage(Page):
	
	def writeHTML(self):
		
		# Retrieve user settings

		self.response().setHeader('Content-Type', 'text/plain')
		self.response().setHeader('Content-Disposition', 'inline')
		
		# Check if remote address is allowed to receive VO-list
		
		remoteAddress = self.request().environ()["REMOTE_ADDR"]
		sessionDir = LapSite.Dirs["SessionDir"]
		voSites = LapSite.Admin["VOSites"]
		
		authorisedSite = False
		
		for site in voSites:
			if remoteAddress.strip() == site.strip():
				authorisedSite = True
				
		if authorisedSite:
			
			# Write out authorised VO-list
		
			voListFilename = os.path.join(sessionDir, "volist.txt")
			
			voList = []
	
			if os.path.exists(voListFilename):
				voListFile = file(voListFilename)
				lines = voListFile.readlines()
				voListFile.close()
				
				for line in lines:
					mapping = re.match('"(.*)"\s*(.*)', line).groups()
					if len(mapping) == 2:
						self.writeln('"'+mapping[0]+'" '+mapping[1])			
