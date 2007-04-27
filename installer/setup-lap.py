#!/bin/env python

#
# Lunarc Application Portal Installer
#
# Copyright (C) 2006-2007 Jonas Lindemann
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

"""Command line and GUI installer for the Lunarc Application Portal.

Start with:

# ./setup-lap.py

for command line setup or:

# ./setup-lap.py gui

for graphical install.
"""

import os, string, sys, shutil, commands, re, types, urllib, pwd

from Tkinter import *

siteInstallDefaultParams = {
	"TargetDir":"/opt",
	"WebWareVersion":"0.9.2",
	"LapVersion":"0.8.0-20061026",
	"LapAppDirName":"lap"
}

siteInstallDefaultDescriptions = {
	"TargetDir":"Target installation directory",
	"WebWareVersion":"WebWare version",
	"LapVersion":"Portal version",
	"LapAppDirName":"Portal application directory name"
}

siteConfigDefaultParams = {
	"LogFile":"/var/log/lap/lap.log",
	"InitLogFile":"/var/log/lap/lap_init.log",
	"WebWareLogFile":"/var/log/lap/lap_ww.log",
	"PluginDir":"/opt/lap/context/Plugins",
	"SessionDir":"/var/spool/lap",
	"WebWareDir":"/opt/Webware-0.9.2",
	"AppWorkDir":"/opt/lap",
	"DependsDir":"/opt/lap/depends",
	"NorduGridDir":"/opt/nordugrid",
	"VOAdmin":"/O=Grid/O=NorduGrid/OU=byggmek.lth.se/CN=Jonas Lindemann",
	"SMTPServer":"mail.lth.se",
	"ServerUser":"apache",
	"ServerGroup":"apache",
	"ServerPIDFile":"/var/run/lap.pid"
}

siteConfigDefaultDescriptions = {
	"LogFile":"Portal log file",
	"InitLogFile":"Portal startup log file",
	"WebWareLogFile":"WebWare log file",
	"PluginDir":"Portal plugin directory",
	"SessionDir":"Portal job session directory",
	"WebWareDir":"WebWare installation directory",
	"AppWorkDir":"Portal installation directory",
	"DependsDir":"Portal dependency installation directory",
	"NorduGridDir":"NorduGrid ARC installation directory",
	"VOAdmin":"Portal Virtual Organisation administrator",
	"SMTPServer":"Default mail server",
	"ServerUser":"Portal user id",
	"ServerGroup":"Portal group id",
	"ServerPIDFile":"Portal process id file"
}

siteConfigTemplate = """Application = {
		"ContextName":"context"
}

Logging = {
		"LogFile":"%(LogFile)s",
		"WebWareLogFile":"%(WebWareLogFile)s"
}

Dirs = {
	"PluginDir":"%(PluginDir)s",
	"SessionDir":"%(SessionDir)s",
	"WebWareDir":"%(WebWareDir)s",
	"AppWorkDir":"%(AppWorkDir)s",
	"DependsDir":"%(DependsDir)s",
	"NorduGridDir":"%(NorduGridDir)s"
}

Appearance = {
		"WelcomeMessage":"Welcome to the LUNARC application portal",
		"WebSiteName":"LUNARC",
		"LogoImage":"images/logo.png",
		"LogoImageWidth":"445px",
		"LogoImageHeight":"86px"
}

Admin = {
		"VOAdmin":"%(VOAdmin)s",
		"VOSites":["130.235.7.91"]
}

System = {
		"SMTPServer":"%(SMTPServer)s",
		"ServerUser":"%(ServerUser)s",
		"ServerGroup":"%(ServerGroup)s",
		"ServerPIDFile":"%(ServerPIDFile)s",
        "ARCInterface":""
}
"""

apacheConfigTemplate = """LoadModule webkit_module modules/mod_webkit.so

<Location /%(Location)s>
WKServer localhost 8086
SetHandler webkit-handler
SSLRequireSSL
</Location>
"""

def centerOnScreen(window):
	"""Centre the window on the screen.  (Actually halfway across
	and one third down.)"""

	window.update_idletasks()
	width = window.winfo_width()
	height = window.winfo_height()
	if width == 1 and height == 1:
		width = window.winfo_reqwidth()
		height = window.winfo_reqheight()

	x = (window.winfo_screenwidth() - width) / 2
	y = (window.winfo_screenheight() - height) / 3
	if x < 0:
		x = 0
	if y < 0:
		y = 0
	window.geometry('+%d+%d' % (x, y))

class StatusWindow:
	"""Window for displaying installation messages.

	If run in command line the class will use print to display messages
	instead."""

	def __init__(self, gui=False):
		"""Class constructor.

		If the gui parameter is set to True a status window will be displayed
		for the status messages."""

		self._gui = gui
		self._visible = False

	def write(self, text=""):
		"""Write status text without line termination."""

		if self._visible and self._gui:
			self._textOutput.insert(END, text)
			self._textOutput.see(END)
			self.update()
		else:
			print text,

	def writeln(self, text=""):
		"""Write status text with line termination."""

		if self._visible and self._gui:
			self._textOutput.insert(END, text+"\n")
			self._textOutput.see(END)
			self.update()
		else:
			print text

	def update(self):
		"""Update the status window. (Process events.)"""

		if self._visible:
			self._window.update()

	def show(self):
		"""Create and show the status window."""

		if self._gui:
			self._window = Tk()
			self._window.title("Installation progress")

			frame = Frame(self._window, bd=5)
			frame.pack(expand=YES, fill=BOTH)
			self._textOutput = Text(frame, height=20, width=80)
			self._textOutput.pack(side=LEFT, fill=BOTH, expand=YES)
			centerOnScreen(self._window)
			self._visible = True
			self._window.update()
		else:
			self._visible = True

	def destroy(self):
		"""Destroy the status window."""

		if self._gui:
			if self._visible:
				self._window.destroy()
				self._visible = False
		else:
			self._visible = False

	def wait(self):
		"""Wait for the user to close the window."""

		if self._gui:
			if self._visible:
				self._window.wait_window()

class OptionInput:
	"""Optional parameter input class.

	This class handles input of installer options in for both the GUI case
	and the command line case."""
	def __init__(self, options = {}, descriptions = {}, caption = "", gui=False, parentWindow=None):
		"""2 dictionaries provide information on the parameter input

		options      - Dictionary containing the option keys and values.
		descriptions - Dictionary containing corresponding option descriptions.
		               The key should be the same as in the options dictionary.
		caption      - Caption for the window or the menu.
		gui          - Determines if the gui or command line versio is used.
		"""

		self._options = options
		self._descriptions = descriptions
		self._caption = caption
		self._gui = gui
		self._parent = parentWindow

		self._dialogResult = False

	def setOptions(self, options):
		"""Set the key/value dictionary used in the dialog."""
		self._options = options

	def setDescriptions(self, descriptions):
		"""Set the description dictionary used in the dialog.

		This dictionary contains the textual descriptions of the option
		parameters."""

		self._descriptions = descriptions

	def setCaption(self, caption):
		"""Set caption for the dialog."""
		self._caption = caption

	def onNext(self):
		"""Event method for handling a click on the next button."""
		self._dialogResult = True
		self._window.destroy()

	def onCancel(self):
		"""Event method for handling a click on the cancel button."""
		self._dialogResult = False
		self._window.destroy()

	def execute(self):
		"""Executes the option parameter dialog."""

		choice = 1

		if self._gui:
			if self._parent == None:
				self._parent = Tk()
			self._window = self._parent
			self._window.title(self._caption)

			self._optionVars = {}

			keys = self._options.keys()
			keys.sort()

			for key in keys:
				self._optionVars[key] = StringVar()
				self._optionVars[key].set(self._options[key])

			number = 1

			for key in keys:
				frame = Frame(self._window, bd=5)
				frame.pack(expand=YES, fill=BOTH)

				row = Frame(frame, bd=2)
				row.pack(expand=NO, fill=BOTH)

				label = Label(row, text=self._descriptions[key], width=30, anchor=W, justify=RIGHT)
				label.pack(side=LEFT)
				textControl = Entry(row, width=30, textvariable=self._optionVars[key])
				textControl.pack(side=LEFT,fill=BOTH,expand=YES)

			row = Frame(frame, bd=2)
			row.pack()

			nextButton = Button(row, text="Next", command = self.onNext)
			nextButton.pack(side=LEFT, pady=4)

			closeButton = Button(row, text="Cancel", command = self.onCancel)
			closeButton.pack(side=LEFT, expand=NO, pady=4)

			#windowHeight = self._window.winfo_height()
			#self._window.geometry("500x%d" % windowHeight)

			centerOnScreen(self._window)
			self._window.mainloop()

			if self._dialogResult == False:
				choice = 0
			else:
				choice = self._options
		else:
			choiceInput = "1"

			# Check max description width

			maxLen = -1

			for key in self._descriptions.keys():
				if len(self._descriptions[key])>maxLen:
					maxLen = len(self._descriptions[key])

			while choice > 0:

				print
				print self._caption
				print
				keys = self._options.keys()
				keys.sort()

				number = 1

				for key in keys:
					print "\t"+str(number)+". "+" "*(2-len(str(number)))+self._descriptions[key]+" "*(maxLen-len(self._descriptions[key])+4)+": "+self._options[key]
					number = number + 1

				print

				choice = -1
				choiceInput = raw_input("Enter option to change. (Enter = accept, 0 = quit) :")

				if choiceInput == '':
					break

				try:
					choice = int(choiceInput)
				except:
					choice = 1
					continue

				print choice

				if choice > 0 and choice <= len(keys):
					print
					print self._descriptions[keys[choice-1]]+" = "+self._options[keys[choice-1]]
					print
					newValue = raw_input("New value (Enter = No Change) : ")

					if newValue<>"":
						self._options[keys[choice-1]] = newValue

		if choice==0:
			return None
		else:
			return self._options

class SystemCheck:
	"""Class for checking the portal requirements."""
	def __init__(self, gui=False):
		"""Class constructor.

		gui - Determines if the class should use a graphical interface or not."""

		self._gui = gui

		self._haveWget = False
		self._haveTar = False
		self._haveUname = False
		self._haveGunzip = False
		self._haveARC = False
		self._haveAPXS = False
		self._haveARCLib = False


		self._arcInstallDir = ""

		self._continueInstall = True

		self._doCheck()

	def _findOnPath(self, executable):
		"""Find an executable on the path and system path.

		This method add /sbin and /usr/sbin to the query."""

		systemPath = os.environ['PATH']
		systemPath = systemPath + ":/sbin:/usr/sbin"

		for item in systemPath.split(':'):
			try:
				if executable in os.listdir(item):
					return True
			except OSError:
				pass

		return False

	def _findPath(self, executable):
		"""Find an executable in the path."""

		systemPath = os.environ['PATH']

		for item in systemPath.split(':'):
			try:
				if executable in os.listdir(item):
					return item
			except OSError:
				pass

		return ""

	def _checkCommand(self, command, alternateText = "", resolution = ""):
		"""Check that a specific command exists.

		The parameter alternateText provides an alternative text that is
		displayed when searching for command. The resolution parameter
		contains a text with a possible resolution for a missing command."""

		if alternateText=="":
			self._textOut("Checking for "+command+". ")
		else:
			self._textOut("Checking for "+alternateText+". ")
		result = self._findOnPath(command)
		if result:
			self._textOutLn("Found.")
		else:
			self._textOutLn("Not found.")
			if resolution !="":
				self._textOutLn()
				self._textOutLn("\t"+resolution)
				self._textOutLn()

		return result

	def _checkInstallDir(self, command, alternateText = "", resolution = ""):
		"""Check that a specific install directory exists.

		The parameter alternateText provides an alternative text that is
		displayed when searching for a install dir. The resolution parameter
		contains a text with a possible resolution for a missing install dir."""

		if alternateText=="":
			self._textOut("Checking for "+command+". ")
		else:
			self._textOut("Checking for "+alternateText+".")
		result = self._findPath(command)
		result = result.split("/bin")[0]

		if result:
			self._arcInstallDir = result
			self._textOutLn("Found.")
		else:
			self._textOutLn("Not found.")
			if resolution !="":
				self._textOutLn()
				self._textOutLn("\t"+resolution)
				self._textOutLn()

		return result

	def _checkARCLib(self):
		"""Check for determining if ARClib is installed."""
		self._textOut("Checking for Python based ARCLib. ")
		if self._arcInstallDir !="":
			# /lib/python2.3/site-packages
			if os.path.isdir(self._arcInstallDir+"/lib/python2.3/site-packages"):
				self._textOutLn("Found.")
				return True
			elif os.path.isdir(self._arcInstallDir+"/lib/python2.4/site-packages"):
				self._textOutLn("Found.")
				return True
			elif os.path.isdir(self._arcInstallDir+"/lib/python2.5/site-packages"):
				self._textOutLn("Found.")
				return True
			else:
				self._textOutLn("Not found.")
				self._textOutLn()
				self._textOutLn("Please add the following packages to the ARC install:")
				self._textOutLn()
				self._textOutLn("\tnordugrid-arc-python-0.6.x")
				self._textOutLn("\tnordugrid-arc-libs-devel-0.6.x")
				self._textOutLn()
		else:
			self._textOutLn("Not found.")
			return True

	def _setupGUI(self):
		"""Sets up the user interface version."""

		self._window = Tk()
		self._window.title("Lunarc Application Portal Requirements")
		frame = Frame(self._window, bd=5)
		frame.pack(expand=YES, fill=BOTH)

		self._haveWgetVar = IntVar()
		self._haveTarVar = IntVar()
		self._haveUnameVar = IntVar()
		self._haveGunzipVar = IntVar()
		self._haveARCVar = IntVar()
		self._haveAPXSVar = IntVar()
		self._haveARCInstallDirVar = IntVar()
		self._haveARCLibVar = IntVar()

		row = Frame(frame, bd=2)
		row.pack(expand=YES, fill=BOTH)

		label = Label(row, text="Testing for")
		label.pack(side=LEFT, expand=NO)

		checkFrame = Frame(frame, bd=2, relief=GROOVE)
		checkFrame.pack(expand=YES, fill=BOTH)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="wget", variable=self._haveWgetVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="tar", variable=self._haveTarVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="uname", variable=self._haveUnameVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="gunzip", variable=self._haveGunzipVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="Advanced Resource Connector ARC", variable=self._haveARCVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="Apache Extension Tool (APXS)", variable=self._haveAPXSVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="ARC install dir", variable=self._haveARCInstallDirVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(checkFrame, bd=2)
		row.pack(expand=NO, fill=BOTH)
		check = Checkbutton(row, text="Python based ARCLib", variable=self._haveARCLibVar, state=DISABLED)
		check.pack(side=LEFT,fill=BOTH,expand=NO)

		row = Frame(frame, bd=2)
		row.pack(expand=NO, fill=BOTH)

		label = Label(row, text="Test result output")
		label.pack(side=LEFT, expand=NO)

		row = Frame(frame, bd=2)
		row.pack(expand=NO, fill=BOTH)

		self._textOutput = Text(row, height=8, width=60)
		self._textOutput.pack(side=LEFT, fill=BOTH, expand=YES)

		row = Frame(frame, bd=2)
		row.pack(side=TOP)

		closeButton = Button(row, text="Close", command = self._onClose)
		closeButton.pack(side=LEFT, pady=4)

		self._installButton = Button(row, text="Install...", command = self._onInstall, state=DISABLED)
		self._installButton.pack(side=LEFT, pady=4)

		centerOnScreen(self._window)

	def _onClose(self):
		"""Event method handling the Close button."""
		self._window.destroy()
		self._continueInstall=False

	def _onInstall(self):
		"""Event method handling the Install button."""
		self._window.destroy()

	def _updateGUI(self):
		"""Manually processes events for Tkinter.

		This method is used in the _doCheck routine for updating
		the user interface."""

		if self._gui:
			self._window.update()

	def _waitGUI(self):
		"""Wait for user interface to finish."""
		if self._gui:
			self._window.wait_window()

	def _textOutLn(self, text=""):
		"""Outputs text with line termination.

		Output goes to the status window during a GUI install otherwise
		it goes to standard output."""

		if self._gui:
			self._textOutput.insert(END, text+"\n")
			self._textOutput.see(END)
			self._window.update()
		else:
			print text

	def _textOut(self, text=""):
		"""Outputs text without line termination.

		Output goes to the status window during a GUI install otherwise
		it goes to standard output."""

		if self._gui:
			self._textOutput.insert(END, text)
			self._textOutput.see(END)
			self._window.update()
		else:
			print text,

	def _doCheck(self):
		"""Method for checking requirements."""

		if self._gui:
			self._setupGUI()
			self._window.update()

		self._textOutLn()
		self._textOutLn("---------------------------------------")
		self._textOutLn("Checking for prerequisites.")
		self._textOutLn("---------------------------------------")
		self._textOutLn()

		self._haveWget = self._checkCommand("wget")
		if self._haveWget and self._gui:
			self._haveWgetVar.set(1)
		self._updateGUI()
		self._haveTar = self._checkCommand("tar")
		if self._haveTar and self._gui:
			self._haveTarVar.set(1)
		self._updateGUI()
		self._haveUname = self._checkCommand("uname")
		if self._haveUname and self._gui:
			self._haveUnameVar.set(1)
		self._updateGUI()
		self._haveGunzip = self._checkCommand("gunzip")
		if self._haveGunzip and self._gui:
			self._haveGunzipVar.set(1)
		self._updateGUI()
		self._haveARC = self._checkCommand("ngsub", "ARC client tools", "Please install the ARC client, see http://www.nordugrid.org.\nor make sure it is correctly installed.")
		if self._haveARC and self._gui:
			self._haveARCVar.set(1)
		self._updateGUI()
		self._haveAPXS = self._checkCommand("apxs", "Apache Extension Tool (APXS)",
											"APXS is needed to build the WebWare apache module. \n\tIt is often found in the httpd-devel package on RedHat derived distros.")
		if self._haveAPXS and self._gui:
			self._haveAPXSVar.set(1)
		self._updateGUI()
		self._arcInstallDir = self._checkInstallDir("ngsub", "ARC installation dir")
		if self._arcInstallDir and self._gui:
			self._haveARCInstallDirVar.set(1)
		self._updateGUI()
		self._haveARCLib = self._checkARCLib()
		if self._haveARCLib and self._gui:
			self._haveARCLibVar.set(1)
		self._updateGUI()

		if self.requirementsOk() and self._gui:
			self._installButton.config(state=NORMAL)

		self._waitGUI()

	def haveWget(self):
		"""Return True if wget is installed."""
		return self._haveWget

	def haveTar(self):
		"""Return True if tar is installed."""
		return self._haveTar

	def haveUname(self):
		"""Return True if uname is installed."""
		return self._haveUname

	def haveGunzip(self):
		"""Return True if gunzip is installed."""
		return self._haveGunzip

	def haveARC(self):
		"""Return True if ARC is installed."""
		return self._haveARC

	def continueInstall(self):
		"""Return True if installation should continue."""
		return self._continueInstall

	def getARCInstallDir(self):
		"""Return ARC install directory."""
		return self._arcInstallDir

	def requirementsOk(self):
		"""Returns True if all requirements are ok."""
		return self._haveWget and self._haveTar and self._haveUname and self._haveGunzip and self._haveARC and self._haveAPXS and self._haveARCLib


class DownloadError(Exception):
	"""Download Error exception."""
	pass

class ExtractionError(Exception):
	"""Extraction Error exception."""
	pass

class Package:
	"""Abstract base class handling a downloadable software package.

	This package is used to specify one or more software packages that is
	to be downloaded and installed during the installation."""
	def __init__(self):
		"""Class constructor."""
		self._targetDir = "./opt"
		self._version = "1.0"
		self._downloadURL = ""
		self._fileList = []
		self._extractTool = "tar"
		self._packageDir = "./packages"
		self._osFlavor = "rhel"
		self._osMajorVersion = 4
		self._osMinorVersion = 4

	def setOS(self, flavor, majorVersion, minorVersion):
		"""Set the OS flavor."""
		self._osFlavor = flavor
		self._osMajorVersion = majorVersion
		self._osMinorVersion = minorVersion

	def getOS(self):
		"""Return OS flavor."""
		return self._osFlavor, self._osMajorVersion, self._osMinorVersion

	def getOSFlavor(self):
		"""Return only OS flavor. No version."""
		return self._osFlavor

	def getOSMajorVersion(self):
		"""Return major OS version."""
		return self._osMajorVersion

	def getOSMinorVersion(self):
		"""Return minor OS version."""
		return self._osMinorVersion

	def setTargetDir(self, targetDir):
		"""Set target directory of installation.

		If the target directory does not exist, it will be created."""
		if not os.path.exists(targetDir):
			os.mkdir(targetDir)
		self._targetDir = targetDir

	def getTargetDir(self):
		"""Return target directory."""
		return self._targetDir

	def setVersion(self, version):
		"""Set software package version."""
		self._version = version

	def getVersion(self):
		"""Return package version."""
		return self._version

	def setDownloadURL(self, downloadURL):
		"""Set URL for downloading the software package."""
		self._downloadURL = downloadURL

	def addFile(self, filename):
		"""Add a file to be downloaded."""
		self._fileList.append(filename)

	def download(self):
		"""Download software packages from specified download URL."""

		if not os.path.exists(self._packageDir):
			os.mkdir(self._packageDir)

		for filename in self._fileList:
			realFilename = filename % self._version
			print "--> " + realFilename + " ",
			if not os.path.exists(os.path.join(self._packageDir, realFilename)):
				url = os.path.join(self._downloadURL, realFilename)
				status = os.system("wget -q -P " + self._packageDir+ " " + url)

				if status == 0:
					print "\t\t[Downloaded]"
				else:
					print "\t\t[Download failed]"
					raise DownloadError()
			else:
				print "\t\t[Exists]"

	def extract(self):
		"""Extract downloaded software packages."""

		if not os.path.exists(self._targetDir):
			os.mkdir(self._targetDir)

		for filename in self._fileList:
			realFilename = filename % self._version
			status = os.system("tar xzf %s -C %s" % (os.path.join(self._packageDir, realFilename), self._targetDir))

			if status <> 0:
				raise ExtractionError()

	def getInstallDir(self, idx):
		"""Return install dir."""
		if idx>=0 and idx<len(self._fileList):
			realFilename = self._fileList[idx] % self._version
			packageDir, ext = os.path.splitext(realFilename)
			packageDir, ext = os.path.splitext(packageDir)
			packageDir = os.path.join(self._targetDir, packageDir)
			return packageDir
		else:
			return ""

	def getDownloadURL(self):
		"""Return download URL."""
		return self._downloadURL

	def setup(self):
		"""Method to be overidden for package specific installation procedures."""
		pass

class WebWare(Package):
	"""WebWare software package."""
	def __init__(self):
		"""Class constructor."""
		Package.__init__(self)
		self._apacheConfigDir = "/etc/httpd"
		self._redhatBased = True
		self.setVersion("0.9.2")
		self.setDownloadURL("http://heanet.dl.sourceforge.net/sourceforge/webware")
		self.addFile("Webware-%s.tar.gz")

	def setApacheConfigDir(self, configDir):
		"""Set apache configuration directory. (default = /etc/httpd)."""
		self._apacheConfigDir = configDir

	def setup(self):
		"""Setup WebWare."""
		realFilename = self._fileList[0] % self._version
		packageDir, ext = os.path.splitext(realFilename)
		packageDir, ext = os.path.splitext(packageDir)
		packageDir = os.path.join(self._targetDir, packageDir)
		print packageDir
		if os.path.exists(packageDir):
			currDir = os.getcwd()
			os.chdir(packageDir)
			os.system("python ./install.py --no-password-prompt")
			os.chdir(currDir)

	def createAppDir(self, appDir):
		"""Create application directory."""
		realAppDir = os.path.abspath(appDir)
		webwareDir = self.getInstallDir(0)
		currDir = os.getcwd()
		os.chdir(webwareDir+"/bin")
		cmd = "./MakeAppWorkDir.py -c context " + realAppDir
		print "Executing, ", cmd
		os.system(cmd)
		os.chdir(currDir)

	def buildApacheModule(self):
		"""Build apache module."""
		webwareDir = self.getInstallDir(0)
		currDir = os.getcwd()
		os.chdir(webwareDir+"/WebKit/Adapters/mod_webkit2")
		print os.system("make")
		print os.system("make install")
		os.chdir(currDir)

class AppPortal(Package):
	"""Lunarc Application Portal software package."""
	def __init__(self):
		Package.__init__(self)
		self._webwareDir = ""
		self._configParams = {}
		self._installParams = {}
		self.setVersion(self.queryLatestVersion())
		self.setDownloadURL("http://grid.lunarc.lu.se/lapsrc")
		self.addFile("lap-config-%s.tar.gz")
		self.addFile("lap-layout-%s.tar.gz")
		self.addFile("lap-plugins-%s.tar.gz")
		self.addFile("lap-source-%s.tar.gz")

	def queryLatestVersion(self):
		"""Query latest version of the portal."""
		try:
			f = urllib.urlopen("http://grid.lunarc.lu.se/lapsrc/lap-latest-version")
			l = f.readlines()
			f.close()
			return l[0].strip()
		except:
			print "Couldn't open url for version query."
			return "0.8.4-20070424"

	def setWebwareDir(self, webwareDir):
		"""Set the location of WebWare."""
		self._webwareDir = webwareDir

	def setConfigParams(self, configParams):
		"""Set configuration parameters."""
		self._configParams = configParams

	def setInstallParams(self, installParams):
		"""Set installation parameters."""
		self._installParams = installParams

	def createSiteConfig(self):
		"""Create portal site configuration.

		The following file is created:
			{Portal install dir}/LapConfig/LapSite.py"""

		configFilename = self._targetDir+"/LapConfig/LapSite.py"

		configFile = file(configFilename, "w")
		configFile.write(siteConfigTemplate % self._configParams)
		configFile.close()

	def updateInitFile(self, rootInstall=False):
		"""Create portal init-script.

		The script is located in {Portal install dir}/init/lap"""

		initFilename = self._targetDir+"/init/lap"

		initFile = file(initFilename, "r")
		lines = initFile.readlines()
		initFile.close()

		# WEBKIT_DIR=/sw/lap
		# PID_FILE=/var/run/lap.pid
		# LOG=/var/log/lap/lap_init.log

		if rootInstall and self.getOSFlavor()=="rhel":
			initFilename = "/etc/init.d/lap"

		initFile = file(initFilename, "w")

		appDirDone = False
		pidFileDone = False
		logFileDone = False

		for line in lines:
			newLine = line
			if line.find("APP_DIR")<>-1 and not appDirDone:
				newLine = "APP_DIR="+self._targetDir+"\n"
				appDirDone = True
			if line.find("PID_FILE")<>-1 and not pidFileDone:
				newLine = "PID_FILE="+self._configParams["ServerPIDFile"]+"\n"
				pidFileDone = True
			if line.find("LOG")<>-1 and not logFileDone:
				newLine = "LOG="+self._configParams["InitLogFile"]+"\n"
				logFileDone = True

			initFile.write(newLine)

		initFile.close()

		if rootInstall and self.getOSFlavor()=="rhel":
			os.system("chkconfig --add lap")

	def createApacheConfig(self, location = "lap", rootInstall = False):
		"""Create apache configuration file.

		If installed as root and on a RedHat system the configuration file
		is created in /etc/httpd/conf.d/ssl_lap.conf."""

		apacheConfigFilename = ""

		print self.getOSFlavor()

		if self.getOSFlavor() == "rhel" and rootInstall:

			# On RedHat we use the conf.d directory to add
			# configuration to the apache web server

			apacheConfigFilename = "/etc/httpd/conf.d/ssl_lap.conf"

		else:

			# For other distros we just create the config file
			# in the current directory

			apacheConfigFilename = "./ssl_lap.conf"

		configFile = file(apacheConfigFilename, "w")
		configFile.write(apacheConfigTemplate % {"Location":location})
		configFile.close()

	def createDirectories(self, rootInstall = False):
		"""Create neccessary portal directories.

		The following directories are created:

		log directory default = /var/log/lap
		init log directory default = /var/log/lap
		webware log directory default = /var/log/lap
		session directory default = /var/spool/lap
		install directory default = /opt/lap"""

		logDir = os.path.split(self._configParams["LogFile"])[0]
		initLogDir = os.path.split(self._configParams["InitLogFile"])[0]
		webwareLogDir = os.path.split(self._configParams["WebWareLogFile"])[0]
		sessionDir = self._configParams["SessionDir"]
		installDir = self.getTargetDir()

		if rootInstall:
			try:
				userInfo = pwd.getpwnam(self._configParams["ServerUser"])
			except KeyError:
				print "Could not setup directories. Server user id not found."
				return
			uid = userInfo[2]
			gid = userInfo[3]
			print uid, gid

			try:
				os.makedirs(logDir)
			except:
				pass

			try:
				os.makedirs(initLogDir)
			except:
				pass

			try:
				os.makedirs(webwareLogDir)
			except:
				pass

			try:
				os.makedirs(sessionDir)
			except:
				pass

			os.chown(logDir, uid, gid)
			os.chown(initLogDir, uid, gid)
			os.chown(webwareLogDir, uid, gid)
			os.chown(sessionDir, uid, gid)
			os.system("chown -R %d.%d %s" % (uid,gid,installDir))

def main(graphicalInstall=False):
	"""Main installation routine.

	When graphicalInstall is set to True a graphical install will
	be performed."""

	installWebWare = True
	downloadPortal = True
	buildApacheModule = True

	rootInstall = False

	if os.geteuid()==0:
		rootInstall = True

	portal = AppPortal()
	webware = WebWare()

	# Check requirements

	systemCheck = SystemCheck(gui=graphicalInstall)
	if not systemCheck.requirementsOk():
		sys.exit(-1)
	if not systemCheck.continueInstall():
		sys.exit(0)

	norduGridDir = systemCheck.getARCInstallDir()

	print
	print "---------------------------------------"
	print "Lunarc Application Portal - Setup 0.1"
	print "---------------------------------------"

	siteInstallDefaultParams["LapVersion"] = portal.getVersion()
	siteInstallDefaultParams["WebWareVersion"] = webware.getVersion()

	installOptions = OptionInput(gui=graphicalInstall)
	installOptions.setOptions(siteInstallDefaultParams)
	installOptions.setDescriptions(siteInstallDefaultDescriptions)
	installOptions.setCaption("Please set the installation options:")
	installParams = installOptions.execute()

	if installParams == None:
		sys.exit(-1)

	installParams["TargetDir"] = os.path.abspath(installParams["TargetDir"])

	sw = StatusWindow(gui=graphicalInstall)
	sw.show()

	sw.writeln()
	sw.writeln()
	sw.writeln("---------------------------------------")
	sw.writeln("Installing WebWare for Python")
	sw.writeln("---------------------------------------")
	sw.writeln()

	webware.setVersion(installParams["WebWareVersion"])
	webware.setTargetDir(installParams["TargetDir"])

	if installWebWare:
		try:
			sw.writeln("Downloading WebWare...")
			webware.download()
			sw.writeln("Extracting WebWare...")
			webware.extract()
			sw.writeln("Setting up WebWare...")
			webware.setup()
		except DownloadError:
			sw.writeln()
			sw.writeln("Failed to download WebWare from:")
			sw.writeln()
			sw.writeln("\t"+webware.getDownloadURL())
			sw.writeln()
			sys.exit(-1)
		except ExtractionError:
			sw.writeln()
			sw.writeln("Failed to extract WebWare.")
			sw.writeln()
			sys.exit(-1)
		except:
			sw.writeln()
			sw.writeln("Unexpected error:", sys.exc_info()[0])
			sw.writeln()

	webwareInstallDir = webware.getInstallDir(0)
	sw.writeln("Webware installed at: "+webwareInstallDir)

	sw.writeln("---------------------------------------")
	sw.writeln("Building WebWare Apache Module")
	sw.writeln("---------------------------------------")
	sw.writeln()

	if buildApacheModule:
		webware.buildApacheModule()

	sw.writeln("---------------------------------------")
	sw.writeln("Creating WebWare application instance")
	sw.writeln("---------------------------------------")
	sw.writeln()

	ApplicationDir = os.path.join(installParams["TargetDir"], installParams["LapAppDirName"])

	sw.writeln("Creating application dir...")
	webware.createAppDir(ApplicationDir)

	sw.writeln("---------------------------------------")
	sw.writeln("Downloading Lunarc Application portal")
	sw.writeln("---------------------------------------")
	sw.writeln()

	portal.setTargetDir(ApplicationDir)
	portal.setVersion(installParams["LapVersion"])

	if downloadPortal:
		try:
			sw.writeln("Downloading portal...")
			portal.download()
			sw.writeln("Extracting portal...")
			portal.extract()
		except DownloadError:
			sw.writeln()
			sw.writeln("Failed to download Portal from:")
			sw.writeln()
			sw.writeln("\t", portal.getDownloadURL())
			sw.writeln()
			sys.exit(-1)
		except ExtractionError:
			sw.writeln()
			sw.writeln("Failed to extract WebWare.")
			sw.writeln()
			sys.exit(-1)
		except:
			sw.writeln()
			sw.writeln("Unexpected error:", sys.exc_info()[0])
			sw.writeln()
			sys.exit(-1)


	sw.writeln()
	sw.writeln("---------------------------------------")
	sw.writeln("Downloading and installing dependencies")
	sw.writeln("---------------------------------------")
	sw.writeln()

	currDir = os.getcwd()
	os.chdir(ApplicationDir)

	status = os.system("./install-depends")
	if status != 0:
		sw.writeln()
		sw.writeln("Dependency install failed.")
		sw.writeln()
		sys.exit(-1)

	os.chdir(currDir)

	sw.writeln()
	sw.writeln("---------------------------------------")
	sw.writeln("Configuring Lunarc Application Portal")
	sw.writeln("---------------------------------------")

	siteConfigDefaultParams["PluginDir"] = os.path.join(ApplicationDir, "context/Plugins")
	siteConfigDefaultParams["WebWareDir"] = os.path.join(installParams["TargetDir"], "Webware-%s" % installParams["WebWareVersion"])
	siteConfigDefaultParams["AppWorkDir"] = ApplicationDir
	siteConfigDefaultParams["DependsDir"] = os.path.join(ApplicationDir, "depends")
	siteConfigDefaultParams["NorduGridDir"] = norduGridDir

	sw.destroy()

	siteConfigInput = OptionInput(gui=graphicalInstall)
	siteConfigInput.setOptions(siteConfigDefaultParams)
	siteConfigInput.setDescriptions(siteConfigDefaultDescriptions)
	siteConfigInput.setCaption("Please set the portal configuration options")
	siteConfigParams = siteConfigInput.execute()

	if siteConfigParams == None:
		sys.exit(-1)

	sw.show()

	sw.writeln()
	sw.writeln("Creating configuration...")

	portal.setConfigParams(siteConfigParams)
	portal.createSiteConfig()
	portal.updateInitFile()
	portal.createApacheConfig(location="lap", rootInstall = rootInstall)
	portal.createDirectories(rootInstall=rootInstall)

	sw.writeln("Installation finished.")
	sw.wait()


if __name__ == "__main__":

	if len(sys.argv)>1:
		if sys.argv[1] == "gui":
			main(graphicalInstall=True)
	else:
		main()
