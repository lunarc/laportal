#
# ApplicationSecurePage base class module
#
# Copyright (C) 2006 Jonas Lindemann
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

"""ApplicationSecurePage module"""

import string, os

from HyperText.HTML import *
from Web.SecurePage import SecurePage

import Web.Ui
import Lap.Version
from Lap.Log import *

import LapSite

from arclib import *

def _orderCompare(x, y):
	return x[3]-y[3]


class ApplicationSecurePage(SecurePage):
	"""Secure application page class (logged in)
	
	Base application class for pages requiring a login."""
	
	# ----------------------------------------------------------------------
	# Private methods
	# ----------------------------------------------------------------------	

	def _findJobPlugins(self):
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
					pluginList.append([entry, fullPath, description])

		return pluginList
	
	def _findVOPlugins(self):
		"""Parse the Plugin directory for VO plugins. Returns
		a list containing available plugins."""
		
		pluginDir = LapSite.Dirs["PluginDir"]
		dirList = os.listdir(pluginDir)
		
		dirList.sort()
		
		pluginList = []
		
		for entry in dirList:
			fullPath = os.path.join(pluginDir, entry)
			if os.path.isdir(fullPath):
				infoFilename = os.path.join(fullPath,"VO.info")
				description = ""
				if os.path.isfile(infoFilename):
					infoFile = file(infoFilename)
					description = infoFile.readline().strip()
					infoFile.close()
					pluginList.append([entry, fullPath, description])

		return pluginList
		
		
	def _findDocPlugins(self):
		"""Parse the Plugin directory for VO plugins. Returns
		a list containing available plugins."""
		
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

	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------					

	def writeContent(self):
		"""Render page and menu."""
	
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

		try:
			proxyCert = Certificate(PROXY, self.session().value("user_proxy"))
			tableBody.append(TR(TD(BR())))
			tableBody.append(TR(TD("User: %s" % proxyCert.GetIdentitySN())))
			tableBody.append(TR(TD("Proxy valid for: %s" % proxyCert.ValidFor())))
		except CertificateError, message:
			self.writeln(message)

		w(table)	

	# ----------------------------------------------------------------------
	# Overidden methods (ApplicationPage)
	# ----------------------------------------------------------------------					

	def onInitMenu(self, menuBar, adapterName):
		"""Initialise menu with static and dynamic menus (plugins)."""
		
		# --- Information menu --- 
		
		menuSession = Web.Ui.Menu(self, "menuSession", "Session", "", width=130)
		menuSession.setHint("Functions for requesting a certificate and authorisation on the systems.")
		menuSession.addMenuItem(Web.Ui.MenuItem("Log out...",self.pageLoc()+"/LogoutPage"))

		menuPreferences = Web.Ui.Menu(self, "menuPreferences", "Settings", "", width=140)
		menuPreferences.setHint("Functions for setting special user preferences.")
		menuPreferences.addMenuItem(Web.Ui.MenuItem("Grid...",self.pageLoc()+"/GridPrefsPage"))
		menuPreferences.addMenuItem(Web.Ui.MenuItem("User...",self.pageLoc()+"/UserPrefsPage"))
		
		if self.isVOAdminUser():
			menuPreferences.addMenuItem(Web.Ui.MenuItem("VO Admin...",self.pageLoc()+"/VOAdminPage"))

		menuCreate = Web.Ui.Menu(self, "menuJobs", "Create", "", width=220)
		menuCreate.setHint("Functions for creating, submitting and managing jobs defined on the portal.")

		jobPluginList = self._findJobPlugins()

		for plugin in jobPluginList:
			pluginName = plugin[0]
			pluginDir = plugin[1]
			pluginDescr = plugin[2]
			menuCreate.addMenuItem(Web.Ui.MenuItem("%s..." % pluginDescr, self.pageLoc()+"/Plugins/%s/CustomJobPage?createjob=0" % (pluginName)))
		
		menuJoin = Web.Ui.Menu(self, "menuJoin", "Join", "", width=170)
		menuJoin.setHint("Functions for joining a specific virtual organisation (VO).")

		voPluginList = self._findVOPlugins()

		for plugin in voPluginList:
			pluginName = plugin[0]
			pluginDir = plugin[1]
			pluginDescr = plugin[2]
			menuJoin.addMenuItem(Web.Ui.MenuItem("%s..." % pluginDescr, self.pageLoc()+"/Plugins/%s/CustomVOPage" % (pluginName)))
			
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
					link=self.pageLoc()+"/Plugins/%s/CustomDocSecurePage" % (pluginName),
					target="_blank",
					windowFeatures="width=%d,height=%d,location=no,menubar=no,toolbar=yes,scrollbars=yes,resizable=yes" % (pluginWidth, pluginHeight)))
			else:
				menuInfo.addMenuItem(
					Web.Ui.MenuItem(caption="%s..." % pluginDescr,
					link=self.pageLoc()+"/Plugins/%s/CustomDocViewSecurePage" % (pluginName),
					target="_blank",
					windowFeatures="width=%d,height=%d,location=no,menubar=no,toolbar=no,scrollbars=yes,resizable=yes" % (pluginWidth, pluginHeight)))

		menuManage = Web.Ui.Menu(self, "menuManage", "Manage", "", width=170)
		menuManage.setHint("Functions for managing jobs")
		menuManage.addMenuItem(Web.Ui.MenuItem("Jobs definitions...",self.pageLoc()+"/ManageJobPage"))
		menuManage.addMenuItem(Web.Ui.MenuItem("Running jobs...",self.pageLoc()+"/PleaseWaitPage?URL=ManageGridJobPage&Message=Querying for jobs..."))
		menuManage.addMenuItem(Web.Ui.MenuItem("Syncronise jobs...",self.pageLoc()+"/PleaseWaitPage?URL=SyncJobsPage&Message=Syncronising job list..."))
		
		menuStorage = Web.Ui.Menu(self, "menuStorage", "Storage", "", width=170)
		menuStorage.setHint("Functions for accessing storage resources")
		menuStorage.addMenuItem(Web.Ui.MenuItem("Query resources...", "http://www.nordugrid.org/monitor/loadmon.php"))
		menuStorage.addMenuItem(Web.Ui.MenuItem("GridFTP client...", self.pageLoc()+"/GridFtpClientPage"))

		menuAbout = Web.Ui.Menu(self, "menuAbout", "About...", self.pageLoc()+"/WelcomePage")
		menuAbout.addMenuItem(Web.Ui.MenuItem("LUNARC...",self.pageLoc()+"/SecureWelcomePage"))
		menuAbout.addMenuItem(Web.Ui.MenuItem("Portal...",self.pageLoc()+"/SecureWelcomePage"))
		
		menuBar.addMenu(menuInfo)
		menuBar.addMenu(menuSession)
		menuBar.addMenu(menuJoin)
		menuBar.addMenu(menuPreferences)
		menuBar.addMenu(menuCreate)
		menuBar.addMenu(menuManage)
		menuBar.addMenu(menuStorage)
		menuBar.addMenu(menuAbout)
		
