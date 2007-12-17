#
# DefaultPage base class module
#
# Copyright (C) 2007 Jonas Lindemann
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

import LapSite

import Ui
import UiExt

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
	
	def expandPageLoc(self, pageName):
		return "%s/%s/%s" % (self.request().adapterName(), LapSite.Application["ContextName"], pageName)
	
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
		
	def addExtControl(self, name, extControl):
		self.__extControls.add(extControl)
		self.__extControlDict[name] = extControl
		
	def addControl(self, name, control):
		self.addExtControl(name, control)
		
	def getExtControl(self, name):
		if self.__extControlDict.has_key(name):
			return self.__extControlDict[name]
		else:
			return None
		
	def getControl(self, name):
		return self.getExtControl(name)
		
	def hasExtControls(self):
		return self.__extControls.controlCount>0
	
	def hasControls(self):
		return self.hasExtControls()

	# ----------------------------------------------------------------------
	# Methods
	# ----------------------------------------------------------------------
	
	def uploadFile(self, fieldName, destDir):
		"""Handles a HTTP file upload request from the
		request file, fieldName, and copies it to the directory
		specified by destDir."""
		if self.request().hasField(fieldName):

			filename = ""

			ok = True
			try:
				f = self.request().field(fieldName)
				fileContent = f.file.read()
				
				
				if f.filename.find("\\")!=-1:
					lapDebug("Explorer upload...")
					
					lastBackslash = f.filename.rfind("\\")
					filename = f.filename[lastBackslash+1:]
					lapDebug("modified filename = " + filename)
				else:
					filename = f.filename
					
				lapDebug("Upload filename = " + filename)
				inputFile = file(os.path.join(destDir, filename), "w")
				inputFile.write(fileContent)
				inputFile.close()
			except:
				ok = False
				pass
			
			if ok:
				lapInfo("File, %s, uploaded to %s." % (filename, destDir))
				return ok, filename
			else:
				return ok, ""
			
		else:
			return False, ""
	

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
	
	def redrawForm(self):
		self.writeBody()
		
	def redraw(self):
		self.writeBody()
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------
	
	def actions(self):
		return Page.actions(self) + self.__extControls.actions
	
	def awake(self, transaction):
		"""Servlet wake-up initialisation
		
		Adds extra code for menubar initialisation. Derived classes should provide
		a onInitMenu routine to initialise the menu."""
		
		Page.awake(self, transaction)

		self.adapterName = self.request().adapterName()
	
	
		self.__extControls = UiExt.Container(self)
		self.__extControlDict = {}
		
		# northPanel = new Ext.Panel({region:'north', contentEl: 'north', height: 52, title: 'Lunarc Application Portal', split:true });
		
		self.__topPanel = UiExt.Panel(self, 'topPanel')
		self.__topPanel.region = "north"
		self.__topPanel.contentEl = "topPanel"
		self.__topPanel.height = 52
		self.__topPanel.title = "Lunarc Application Portal"
		
		self.__mainPanel = UiExt.Panel(self, 'mainPanel')
		self.__mainPanel.region = "center"
		self.__mainPanel.contentEl = "mainPanel"
		
		# westPanel = new Ext.Panel({region:'west', id:'west-panel', split:true, width: 200, minSize: 175, maxSize: 400, collapsible: true, margins:'0 0 0 5', layout:'accordion', layoutConfig:{ animate:true }});
		
		self.__appPanel = UiExt.Panel(self, 'appPanel')
		self.__appPanel.region = "west"
		self.__appPanel.contentEl = "appPanel"
		self.__appPanel.width = 200
		self.__appPanel.maxSize = 400
		self.__appPanel.minSize = 200
		self.__appPanel.collapsible = True
		self.__appPanel.layout = 'accordion'
		self.__appPanel.animate = True
		
		# jobTypePanel = new Ext.Panel({title:'Job types', border:false, iconCls:'nav'});

		# southPanel = new Ext.Panel({region:'south', contentEl: 'south', split:true, height: 30, collapsible: true, margins:'0 0 0 0'});
		
		self.__bottomPanel = UiExt.Panel(self, 'bottomPanel')
		self.__bottomPanel.region = "south"
		self.__bottomPanel.contentEl = "bottomPanel"
		self.__bottomPanel.height = 30
		
		self.__viewport = UiExt.Viewport(self, 'viewport')
		self.__viewport.add(self.__topPanel)
		self.__viewport.add(self.__mainPanel)
		self.__viewport.add(self.__appPanel)
		self.__viewport.add(self.__bottomPanel)
		
		self.__toolbar = UiExt.Toolbar(self, 'lapToolbar')

		# Add menu bar as a special non renderable object to
		# the ExtJS container object
		
		self.__extControls.addSystem(self.__toolbar)
		self.__extControls.addSystem(self.__viewport)

		self.onInitToolbar(self.__toolbar, self.adapterName)
		self.onInitAppPanel(self.__appPanel, self.adapterName)
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
		
		if self.onIncludeLapCSS():
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/css/lap.css"))
		if self.onIncludeUiCSS():
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/css/ui.css"))

		extraCSS = self.onAdditionalCSS()

		for css in extraCSS:
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+css))

		if self.onIncludeAdditionalJavaScript():
			self.writeln(self.onGetAdditionalJavaScript())
			
		if self.onUseExtJS():
			self.writeln(LINK(rel="stylesheet",href=self.pageLoc()+"/ext/resources/css/ext-all.css"))
			self.writeln(SCRIPT(type="text/javascript", src=self.pageLoc()+"/ext/adapter/ext/ext-base.js"))
			self.writeln(SCRIPT(type="text/javascript", src=self.pageLoc()+"/ext/ext-all.js"))
			
		if self.onUseExtJS():
			"""Render code needed for the ExtJS controls."""
			self.writeln(SCRIPT(self.__extControls.renderJSToString(), type="text/javascript"))
		
	def htBodyArgs(self):
		"""Provide body arguments for the page
		
		if onUseMenu() returns True, routines for initialising the menubar
		is added in the body arguments.
		"""
		return 'color=black bgcolor=white'
		
	def writeBodyParts(self):
		"""Write the body parts of the page
		
		Writes the different parts of the portal page. Several routines
		"""
		if self.onUseContentDiv():
			self.writeln('<DIV id="%s" style="padding: 20px 20px 20px 20px;">' % "mainPanel")
			if self.onUseExtJS():
				print "Rendering EXT controls."
				self.onBeforeRender(self.request().adapterName())
				self.__extControls.render()
				self.onAfterRender(self.request().adapterName())
				if not self.hasExtControls():
					self.writeContent()
			else:
				self.writeContent()
			self.writeln('</DIV>')
			self.writeln('<DIV id="%s">' % "topPanel")
			if self.onUseMenu():
				self.__toolbar.render()
			self.writeln('</DIV>')
			
			self.__appPanel.render()
			
			self.writeln('<DIV id="%s"><CENTER>Lunarc Application Portal 1.0</CENTER></DIV>' % "bottomPanel")
		else:
			if self.onUseExtJS():
				print "Rendering EXT controls."
				self.onBeforeRender(self.request().adapterName())
				self.__extControls.render()
				self.onAfterRender(self.request().adapterName())
				if not self.hasExtControls():
					self.writeContent()
			else:
				self.writeContent()

			
		if self.onUseTooltips():
			self.writeln(Ui.tooltipJavaScript)
			
	# ----------------------------------------------------------------------
	# DefaultPage Event methods (Callbacks)
	# ----------------------------------------------------------------------						
			
	def onInitAppPanel(self, appPanel, adapterName):
		pass
	
	def onInitToolbar(self, toolbar, adapterName):
		pass
	
	def onInit(self, adapterName):
		"""This function is called when a servlet is woken up.
		
		Use this function to instanciate classes needed for servlet
		operation."""
		pass
	
	def onBeforeRender(self, adapterName):
		pass
	
	def onAfterRender(self, adapterName):
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
		return False
	
	def onGetContentDivId(self):
		"""Return name of content div. Default "workarea"."""
		return "centerPanel"
	
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
		return True
		



	
		
