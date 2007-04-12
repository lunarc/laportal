"""ApplicationPage module"""

import string, os

from HyperText.HTML import *
from Web.DefaultPage import DefaultPage

import Web.Ui
import Lap.Version

import LapSite

def _orderCompare(x, y):
	return x[3]-y[3]

class ApplicationPage(DefaultPage):
	"""Application page class (Not logged in)
	
	Base class for public pages not needing a login"""

	def _findDocPlugins(self):
		"""Find available documentation plugins
		
		Returns a list of plugin information. Each item in the list consists of:
		
		Plugin name (string)
		Full path to plugin (string)
		Plugin description (string)
		Plugin order (int)
		Width of popup window (int)
		Height of popup window (int)
		Documentation type html|pdf (string)
		"""
		
		pluginDir = LapSite.Dirs["PluginDir"]
		dirList = os.listdir(pluginDir)
		
		dirList.sort()
		
		pluginList = []
		
		for entry in dirList:
			fullPath = os.path.join(pluginDir, entry)
			if os.path.isdir(fullPath):
				infoFilename = os.path.join(fullPath,"Doc.info")
				description = ""
				if os.path.isfile(infoFilename):
					infoFile = file(infoFilename)
					description = infoFile.readline().strip()
					order = int(infoFile.readline().strip())
					width = int(infoFile.readline().strip())
					height = int(infoFile.readline().strip())
					docType = infoFile.readline().strip()
					infoFile.close()
					pluginList.append([entry, fullPath, description, order, width, height, docType])
					
		pluginList.sort(_orderCompare)

		return pluginList
	
	def writeContent(self):
		"""Render page"""
	
		wr = self.writeln
		w = self.write
		
		welcomeMessage = """<strong>%s</strong>""" % LapSite.Appearance["WelcomeMessage"]
		
		table = TABLE(style="font-family: tahoma; font-size: 10pt", width="80%")
		tableBody = TBODY()
		table.append(tableBody)
		tableBody.append(TR(TD(welcomeMessage)))
		tableBody.append(TR(TD(BR())))
		if Lap.Version.textVersion!="":
			tableBody.append(TR(TD("LAP Version %d.%d.%d (%s)" % (Lap.Version.majorVersion, Lap.Version.minorVersion, Lap.Version.releaseVersion, Lap.Version.textVersion))))
		else:
			tableBody.append(TR(TD("LAP Version %d.%d.%d " % (Lap.Version.majorVersion, Lap.Version.minorVersion, Lap.Version.releaseVersion))))
		tableBody.append(TR(TD("%s" % Lap.Version.copyright)))
		tableBody.append(TR(TD("Distributed under the %s" % Lap.Version.license)))
		tableBody.append(TR(TD("Written by: %s" % Lap.Version.author)))
		tableBody.append(TR(TD(BR())))
		tableBody.append(TR(TD("Credits:")))
		tableBody.append(TR(TD(BR())))
		tableBody.append(TR(TD(Lap.Version.credits1)))
		tableBody.append(TR(TD(Lap.Version.credits2)))
		tableBody.append(TR(TD(Lap.Version.credits3)))
		tableBody.append(TR(TD(Lap.Version.credits4)))

		w(table)	

	def onInitMenu(self, menuBar, adapterName):
		"""Initialize main menu
		
		Creates the initial menu for the portal when the user is
		not logged in."""
		
		# --- Information menu --- 
		
		menuInformation = Web.Ui.Menu(self, "menuInformation", "Information", "")
				
		menuInformationDocs = Web.Ui.Menu(self, "menuInformationDocs", "Documentation", "")
		menuInformationDocs.setWidth(300)
		menuInformationDocs.addMenuItem(Web.Ui.MenuItem("Getting started",""))
		menuInformationDocs.addMenuItem(Web.Ui.MenuItem("User's guide",""))
		menuInformationDocs.addMenuItem(Web.Ui.MenuItem("Programmer's guide",""))
		
		menuInformation.addSubmenu(Web.Ui.MenuItem("Documentation", ""), menuInformationDocs)
		
		menuInformationSoftware = Web.Ui.Menu(self, "menuInformationSoftware", "Software", "")
		menuInformationSoftware.addMenuItem(Web.Ui.MenuItem("Handling .tar.gz-files (7zip)",""))
		menuInformationSoftware.addMenuItem(Web.Ui.MenuItem("Proxy generation (CoG 1.1)",""))
		
		menuInformation.addSubmenu(Web.Ui.MenuItem("Documentation", ""), menuInformationSoftware)
		
		menuSession = Web.Ui.Menu(self, "menuSession", "Session", "")
		menuSession.setHint("Functions for requesting a certificate and authorisation on the systems.")
		menuSession.addMenuItem(Web.Ui.MenuItem("Log in...",self.pageLoc()+"/LoginPageDummy"))

		menuAbout = Web.Ui.Menu(self, "menuAbout", "About...", self.pageLoc()+"/WelcomePage")
		menuAbout.addMenuItem(Web.Ui.MenuItem("LUNARC...",self.pageLoc()+"/WelcomePage"))
		menuAbout.addMenuItem(Web.Ui.MenuItem("Portal...",self.pageLoc()+"/WelcomePage"))
		
		menuInfo = Web.Ui.Menu(self, "menuInfo", "Information", "", width=170)
		menuInfo.setHint("Installed documentation")

		docPluginList = self._findDocPlugins()

		for plugin in docPluginList:
			pluginName = plugin[0]
			pluginDir = plugin[1]
			pluginDescr = plugin[2]
			pluginOrder = plugin[3]
			pluginWidth = plugin[4]
			pluginHeight = plugin[5]
			pluginDocType = plugin[6]
			if pluginDocType == "html":
				menuInfo.addMenuItem(
					Web.Ui.MenuItem(caption="%s..." % pluginDescr,
					link=self.pageLoc()+"/Plugins/%s/CustomDocPage" % (pluginName),
					target="_blank",
					windowFeatures="width=%d,height=%d,location=no,menubar=no,toolbar=yes,scrollbars=yes,resizable=yes" % (pluginWidth, pluginHeight)))
			else:
				menuInfo.addMenuItem(
					Web.Ui.MenuItem(caption="%s..." % pluginDescr,
					link=self.pageLoc()+"/Plugins/%s/CustomDocViewPage" % (pluginName),
					target="_blank",
					windowFeatures="width=%d,height=%d,location=no,menubar=no,toolbar=no,scrollbars=yes,resizable=yes" % (pluginWidth, pluginHeight)))
				
		
		menuBar.addMenu(menuInfo)
		menuBar.addMenu(menuSession)
		menuBar.addMenu(menuAbout)
		
