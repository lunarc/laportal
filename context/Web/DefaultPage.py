#
# DefaultPage base class module
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

"""DefaultPage module

Contains the abstract base class for the default Lap page.
"""

from WebKit.Page import Page
from Web.Security import FieldValidationMixin

import string, os, re

from HyperText.HTML import *

import Ui
import Lap.Utils

import LapSite

class DefaultPage(Page, FieldValidationMixin):
	"""Abstract base class for all pages in the portal.
	
	By overriding the onXXX methods in this class the behavior of the
	derived page can be controlled. The class also adds fieldvalidation
	routines from the FieldValidationMixin class."""

	# ----------------------------------------------------------------------
	# Get/set methods
	# ----------------------------------------------------------------------		
	
	def getPageName(self):
		"""Convenience function returning the name of the
		page class."""
		
		className = str(self.__class__)
		classParts = className.split("'")
		classParts2 = classParts[1].split(".")
		return classParts2[len(classParts2)-1]
	
	def getProperty(self, key):
		"""Return the value of the session property 'key'. If not
		found the function returns None."""
		
		modifiedKey = self.getPageName()+"_"+key
		return self.getSessionValue(modifiedKey)
	
	def getPageProperty(self, page, key):
		"""Return the value of the session property 'key'. If not
		found the function returns None."""
		
		modifiedKey = page+"_"+key
		return self.getSessionValue(modifiedKey)
	
	def setProperty(self, key, value):
		"""Sets the property value. If the property does not exist
		it will be added."""
		
		modifiedKey = self.getPageName()+"_"+key
		self.session().setValue(modifiedKey, value)
		
	def getSessionValue(self, key):
		"""Returns the session value determined by, 'key'."""
		if self.session().hasValue(key):
			return self.session().value(key)
		else:
			return None
		
	def addExtControl(self, extControl):
		self._extControls.append(extControl)

	# ----------------------------------------------------------------------
	# Methods
	# ----------------------------------------------------------------------		

	def hasProperty(self, key):
		"""Returns True if the page class has the property, 'key'."""
		
		modifiedKey = self.getPageName()+"_"+key
		return self.session().hasValue(modifiedKey)
		
	def delProperty(self, key):
		"""Deletes the property, 'key'."""
		
		modifiedKey = self.getPageName()+"_"+key
		if self.session().hasValue(modifiedKey):
			self.session().delValue(key)	

	def pageLoc(self):
		"""Returns the absolute page address."""
		return "%s/%s" % (self.request().adapterName(), LapSite.Application["ContextName"])
	
	def contextDir(self):
		"""Returns the true workind directory of the application"""
		return "%s/%s" % (LapSite.Dirs["AppWorkDir"], LapSite.Application["ContextName"])
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			
	
	def awake(self, transaction):
		"""Servlet wake-up initialisation
		
		Adds extra code for menubar initialisation. Derived classes should provide
		a onInitMenu routine to initialise the menu."""
		
		Page.awake(self, transaction)

		self.adapterName = self.request().adapterName()
		
		self.menuBar = Ui.MenuBar(self, self.pageLoc())
		
		if self.onUseAlternateMenu():
			self.menuBar.enableAlternateMenu()
		else:
			self.menuBar.disableAlternateMenu()
			
		self.menuBar.setPosition(0,90)
		self.menuBar.setFullWidth(True)
		
		self._extControls = []
		self.onInitMenu(self.menuBar, self.adapterName)
		self.onInit(self.adapterName)
		
	def writeBody(self):
		"""Write the body parts of the page
		
		calls htBodyArgs() for any body arguments.
		"""
		wr = self.writeln
		bodyArgs = self.htBodyArgs()
		if bodyArgs:
			wr('<body %s>' % bodyArgs)
		else:
			wr('<body>')
			
		self.writeBodyParts()
		wr('</body>')
		self.writeFooter()
		
	def writeFooter(self):
		"""Write a page footer"""
		pass
			
	def writeStyleSheet(self):
		"""Write stylesheet code
		
		Adds stylesheets includes needed for the portal. Several routines
		control the behavior of this routine, see 
		onIncludeMenuCSS(), onIncludeLapCSS(), onIncludeUiCSS(),
		onAdditionalCSS(), onIncludeMenuJavaScript().
		"""
		
		if self.onIncludeMenuCSS():
			if self.onUseAlternateMenu():
				pass
			else:
				self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/transmenu/transmenu.css"))
		if self.onIncludeLapCSS():
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/css/lap.css"))
		if self.onIncludeUiCSS():
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/css/ui.css"))

		extraCSS = self.onAdditionalCSS()

		for css in extraCSS:
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+css))

		if self.onIncludeMenuJavaScript():
			self.menuBar.renderJavaScript()
			
		if self.onIncludeAdditionalJavaScript():
			self.writeln(self.onGetAdditionalJavaScript())
			
		#<link rel="stylesheet" type="text/css" href="../../resources/css/ext-all.css" />
		#<script type="text/javascript" src="../../adapter/yui/yui-utilities.js"></script>
		#<script type="text/javascript" src="../../adapter/yui/ext-yui-adapter.js"></script>
		#<script type="text/javascript" src="../../ext-all.js"></script>
			
		if self.onUseExtJS():
			#self.writeln('<LINK rel="stylesheet",href="'+self.pageLoc()+'/ext/resources/css/ext-all.css"/>')
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/ext/resources/css/ext-all.css"))
			self.writeln(SCRIPT(type="text/javascript", src=self.pageLoc()+"/ext/adapter/yui/yui-utilities.js"))
			self.writeln(SCRIPT(type="text/javascript", src=self.pageLoc()+"/ext/adapter/yui/ext-yui-adapter.js"))
			self.writeln(SCRIPT(type="text/javascript", src=self.pageLoc()+"/ext/ext-all.js"))
			
		if self.onUseExtJS():
			"""Render code needed for the ExtJS controls."""
			
			# First render the OnReady function with declarations for each control.
			
			onReadyString = ""
			
			for extControl in self._extControls:
				onReadyString += extControl.getOnReadyInit() + "\n\n"

			onReadyString = "Ext.onReady(function() {\n"+onReadyString+"\n});\n\n"
			
			extOnReadyScript = SCRIPT(onReadyString, type="text/javascript")
			self.writeln(extOnReadyScript)
			
			# Render the different JavaScript additions needed for each control.
				
			for extControl in self._extControls:
				extScript = SCRIPT(extControl.getJavaScript(), type="text/javascript")
				self.writeln(extScript)

		
	def htBodyArgs(self):
		"""Provide body arguments for the page
		
		if onUseMenu() returns True, routines for initialising the menubar
		is added in the body arguments.
		"""
		if self.onUseMenu():
			if self.onUseAlternateMenu():
				return 'color=black bgcolor=white onload="initjsDOMenu()"'
			else:
				return 'color=black bgcolor=white onload="init()"'
		else:
			return 'color=black bgcolor=white'
		
	def writeBodyParts(self):
		"""Write the body parts of the page
		
		Writes the different parts of the portal page. Several routines
		"""

		if self.onUseLogo():
			logoImage = LapSite.Appearance["LogoImage"]
			logoImageWidth = LapSite.Appearance["LogoImageWidth"]
			logoImageHeight = LapSite.Appearance["LogoImageHeight"]
	
			self.writeln(IMG(src="%s/%s" % (self.pageLoc(), logoImage),
				style="position:absolute; left:0px; top:0px; width: %s; height: %s;"
				% (logoImageWidth, logoImageHeight)))
			
		if self.onUseMenu():
		
			if self.onUseAlternateMenu():
				self.menuBar.enableAlternateMenu()
			else:
				self.menuBar.disableAlternateMenu()
		
			self.menuBar.render()	
			self.menuBar.renderBodyJavaScript()

		if self.onUseContentDiv():
			contentDivId = self.onGetContentDivId()
		
			self.writeln('<DIV id="%s">' % contentDivId)
			self.writeContent()
			self.writeln('</DIV>')
		else:
			self.writeContent()

			
		if self.onUseTooltips():
			
			self.writeln(Ui.tooltipJavaScript)
			
	# ----------------------------------------------------------------------
	# DefaultPage Event methods (Callbacks)
	# ----------------------------------------------------------------------						
			
	def onInitMenu(self, menuBar, adapterName):
		"""This function is called when the menuBar is created.

		Use the menuBar instance to fill the menu with menus.
		"""
		pass
	
	def onInit(self, adapterName):
		"""This function is called when a servlet is woken up.
		
		Use this function to instanciate classes needed for servlet
		operation."""
		pass
	
	def onUseLogo(self):
		"""Override to change logo behavior. 

		Return False to disable logo. (Default True)"""
		return True
	
	def onUseMenu(self):
		"""Override to change menu behavior. 

		Return False to disable menu. (Default True)"""
		return True
	
	def onUseTooltips(self):
		"""Override to change tooltip behavior. 

		Return False to disable tooltips. (Default True)"""
		return True
	
	def onGetContentDivId(self):
		"""Return name of content div. Default "workarea"."""
		return "workarea"
	
	def onUseContentDiv(self):
		"""Override to change content div usage. 

		Return False to disable content div rendering. (Default True)"""
		return True

	def onIncludeLapCSS(self):
		"""Overide to change Lap CSS inclusion.

		Return False to disable Lap CSS include. (Default True)"""
		return True

	def onIncludeUiCSS(self):
		"""Override to change Ui CSS inclusion.

		Return False to disable Lap CSS include. (Default True)"""
		return True

	def onIncludeMenuCSS(self):
		"""Override to change Menu CSS inclusion.

		Return False to disable Menu CSS include. (Default True)"""
		return True

	def onIncludeMenuJavaScript(self):
		"""Override to disable menu javascript code.

		Return False to disable menu javascript. (Default True)"""
		return True

	def onAdditionalCSS(self):
		"""Additional CSS includes.

		Return a list with additional CSS includes. (Default = empty list [])"""
		return []
	
	def onUseAlternateMenu(self):
		"""Override use of alternate menu.

		Return False to disable rendering of alternate menu. (Default True)
		(Note: this routine will be obsolete in coming versions of Lap.
		"""
		return True
	
	def onIncludeAdditionalJavaScript(self):
		"""Override to enable additional JavaScripts
		
		Return True to enable JavaScript rendering. (Default False)"""
		return False
	
	def onGetAdditionalJavaScript(self):
		"""Override to add additional Javascript code to the page."""
		return ""
	
	def onUseExtJS(self):
		return False
		



	
		
