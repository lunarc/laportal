#
# Ui module
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

"""User interface module.

This module defines the basic user interface components used in Lap. 
"""

import os
import sys

from HyperText.HTML import *

import Utils
import Templates

from Web.UiTemplates import *
from Web.Security import FieldValidationMixin

from WebKit.Page import Page

class MenuItem:
	"""Menu item class.

	Defines a menu item for use with the Menu and MenuBar classes.
	"""
	def __init__(self, caption="defaultMenuItem", link="", hint="", target="", windowTitle="", windowFeatures=""):
		"""Constructor

		The most common parameters can be set from the MenuItem constructor.

		@param caption: Menu item caption, the text displayed.
		@param link: The menu item URL.
		@param hint: The menu item hint text.
		@param target: The target of the menu item URL. Currently only _blank is implemented.
		@param windowTitle: Title of the window to be opened if target = _blank.
		@param WindowFeatures: Window features of the opened window if target = _blank. 
		"""
		self.caption = caption
		self.link = link
		self.hint = hint
		self.subMenu = None
		self.target = target
		self.windowTitle = windowTitle
		self.windowFeatures = windowFeatures
	
	def setCaption(self, caption):
		"""Set menu item caption. Text displayed in menu."""
		self.caption = caption
		
	def getCaption(self):
		"""Return menu item caption."""
		return self.caption
	
	def setLink(self, link):
		"""Set menu item URL."""
		self.link = link
		
	def getLink(self):
		"""Return menu item URL."""
		return self.link
	
	def setHint(self, hint):
		"""Set menu item hint text."""
		self.hint = hint
		
	def getHint(self):
		"""Return menu item hint text."""
		return self.hint
	
	def setSubmenu(self, menu):
		"""Not fully implemented yet..."""
		self.subMenu = menu
		
	def getSubmenu(self):
		"""Not fully implemented yet..."""
		return self.subMenu
		
	def setTarget(self, target):
		"""Set menu item target of menu item URL. Currently only _blank is implemented."""
		self.target = target
		
	def getTarget(self):
		"""Return menu item target."""
		return self.target
	
	def setWindowFeatures(self, features):
		"""Set the window features of the window opened when target = _blank."""
		self.windowFeatures = features
		
	def getWindowFeatures(self):
		"""Return the window features."""
		return self.windowFeatures
		
	def isSubmenu(self):
		"""Returns true if menu item is a submenu."""
		return self.subMenu!=None

class Menu:
	"""Single drop down menu.

	Implements a single drop down menu with a set of MenuItem instances. This class
	is used in conjunction with the MenuBar class."""
	def __init__(self, page, name="defaultMenu", caption="default", link="", slide="down", x=0, y=0, width=100, height=100):
		"""Constructor

		@param page: WebKit Page instance containing the menu. Used for HTML rendering.
		@param name: Unique menu name. Used in javascript variable instances.
		@param caption: Menu caption. Drop down caption text.
		"""
		self.name = name
		self.slide = slide
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.page = page
		self.hint = ""
		self.link = link
		self.caption = caption
		self.separator = False
		self.subMenu = False
		self.menuItems = []
		self.parentMenu = None
		self.target = ""
		
	def addMenuItem(self, menuItem):
		"""Add a MenuItem to the menu."""
		self.menuItems.append(menuItem)
		
	def addSubmenu(self, menuItem, menu):
		"""Add a submenu to a specific menu item."""
		menuItem.setSubmenu(menu)
		self.menuItems.append(menuItem)
		
	def setSubmenu(self, flag):
		"""Set flag for indicating that the menu is a sub menu."""
		self.subMenu = flag
		
	def isSubmenu(self):
		"""Return True of menu is a submenu."""
		return self.subMenu
	
	def setParentMenu(self, menu):
		"""Set parent menu for a submenu."""
		self.parentMenu = menu
		
	def getParentMenu(self):
		"""Return parent menu for a submenu."""
		return self.parentMenu
	
	def setSeparator(self, flag):
		"""Determines if the menu item should be separator or not."""
		self.separator = flag
		
	def isSeparator(self):
		"""Returns true if menu is a separator."""
		return self.separator
	
	def setHint(self, hint):
		"""Sets the menu hint message."""
		self.hint = hint
		
	def getHint(self):
		"""Returns the menu hint message."""
		return self.hint
		
	def setLink(self, link):
		"""Sets the menu link URL."""
		self.link = link
		
	def getLink(self):
		"""Return the menu link URL."""
		return self.link
	
	def setCaption(self, caption):
		"""Set the menu caption."""
		self.caption = caption
		
	def getCaption(self):
		"""Return the menu item caption."""
		return self.caption
	
	def setName(self, name):
		"""Set the menu name."""
		self.name = name
	
	def getName(self):
		"""Return menu name."""
		return self.name
	
	def setPosition(self, x, y):
		"""Set menu item position, if applicable."""
		self.x = x
		self.y = y
		
	def setWidth(self, width):
		"""Set menu item width."""
		self.width = width
		
	def getWidth(self):
		"""Return menu item width."""
		return self.width
		
	def getLeft(self):
		"""Return menu left position (=x)."""
		return self.x
	
	def getTop(self):
		"""Return menu top position (=y)."""
		return self.y
	
	def setTarget(self, target):
		"""Set menu URL target."""
		self.target = target
	
	def getMenuItems(self):
		"""Return list of menu items."""
		return self.menuItems
	
	def getSize(self):
		"""Return number of menu items."""
		return len(self.menuItems)
	
	def renderJavaScript(self, parentName = "", idx = -1):
		"""Render needed java script code for the menu."""
		
		if parentName == "":
			parent = "ms"
		else:
			parent = parentName
		
		if parent == "ms":
			self.page.writeln('var var%(name)s = %(parentName)s.addMenu(document.getElementById("%(name)s"));' %
							  { "name":self.getName(), "parentName":parent} );
		else:
			self.page.writeln('var submenu = %(parentName)s.addMenu(%(parentName)s.items[%(idx)d]);' %
							  { "name":self.getName(), "parentName":parent, "idx":idx });
			
		menuCount = 0
		
		for menuItem in self.menuItems:
			if not menuItem.isSubmenu():
				if parent == "ms":
					self.page.writeln('var%(name)s.addItem("%(caption)s", "%(link)s", "%(target)s", "%(windowFeatures)s");' %
									  {"name":self.getName(), "caption":menuItem.getCaption(), "link":menuItem.getLink(),
									   "target":menuItem.getTarget(), "windowFeatures":menuItem.getWindowFeatures()})
				else:
					self.page.writeln('submenu.addItem("%(caption)s", "%(link)s", "%(target)s", "%(windowFeatures)s");' %
									  {"name":self.getName(), "caption":menuItem.getCaption(), "link":menuItem.getLink(),
									   "target":menuItem.getTarget(), "windowFeatures":menuItem.getWindowFeatures()})
			else:
				self.page.writeln('var%(name)s.addItem("%(caption)s", "%(link)s", "%(target)s", "%(windowFeatures)s");' %
								  {"name":self.getName(), "caption":menuItem.getCaption(), "link":menuItem.getLink(),
								   "target":menuItem.getTarget(), "windowFeatures":menuItem.getWindowFeatures()})
				menuItem.getSubmenu().renderJavaScript("var%s" % self.getName(), menuCount)
				
			menuCount = menuCount + 1
		
	
class MenuBar:
	"""MenuBar class
	
	The MenuBar class implements a complete javascript based menubar. The class
	can render code for both the JsMenu javascript menu and Transmenu javascript
	menu."""
	def __init__(self, page, scriptDir):
		"""Class constructor.
		
		The page parameter is the WebKit page on which the menu is
		to be rendered. The scriptDir contains the location of the javascript
		code."""
		
		self.page = page
		self.menus = []
		self.subMenus = []
		
		self.left = 20
		self.top = 20
		self.width = 120
		
		self.fullWidth = False
		
		self.scriptDir = scriptDir
		
		self.alternateMenu = True
		self.divId = ""
		
	def setPosition(self, left, top):
		"""Set menu position."""
		self.left = left
		self.top = top
		
	def setWidth(self, width):
		"""Set menu width."""
		self.width = width
		
	def setFullWidth(self, flag):
		"""Set to True if the menu should expand to the entire browser width."""
		self.fullWidth = flag
	
	def getFullWidth(self):
		"""Return True if the menu uses the entire browser width."""
		return self.fullWidth
	
	def enableAlternateMenu(self):
		"""Enable alternate menu implementation (default=True)."""
		self.alternateMenu = True
		
	def disableAlternateMenu(self):
		"""Disable alternate menu implementation (default=False)."""
		self.alternateMenu = False
		
	def addMenu(self, menu):
		"""Add menu to menu bar."""
		self.menus.append(menu)
		
	def addSubmenu(self, menu):
		"""Add sub menu to menu bar."""
		self.subMenus.append(menu)
		
	def addSeparator(self):
		"""Add separator to menu bar."""
		menu = Menu(self.page)
		menu.setSeparator(True)
		self.addMenu(menu)
		
	def setDivId(self, id):
		"""Set id for div."""
		self.divId = id
		
	def renderJsMenuBarFunc(self):
		"""Render javascript code for the JsMenubar."""
		
		self.page.write('<script type="text/javascript">\n')
		self.page.write('function createjsDOMenu() {\n')
		
		for menu in self.menus:
			self.page.write('%s = new jsDOMenu(%d, "absolute");\n' % (menu.getName(), menu.getWidth()))
			
			self.page.write('with (%s) {\n' % (menu.getName()))
			for menuItem in menu.getMenuItems():
				if menuItem.getTarget()=="_blank":
					params = "code:window.open('%s', '', '%s')" % (menuItem.getLink(), menuItem.getWindowFeatures())
					self.page.write('addMenuItem(new menuItem("%s", "", "%s"));\n' % (menuItem.getCaption(), params))
				else:
					self.page.write('addMenuItem(new menuItem("%s", "", "%s"));\n' % (menuItem.getCaption(), menuItem.getLink()))
			self.page.write('}\n')
			
		self.page.write('absoluteMenuBar = new jsDOMenuBar();\n')
			
		self.page.write('with (absoluteMenuBar) {\n')
		for menu in self.menus:
			self.page.write('addMenuBarItem(new menuBarItem("%s", %s));\n' % (menu.getCaption(), menu.getName()))
		
		if self.divId=="":
			self.page.write('moveTo(%d, %d);\n' % (self.left, self.top))
		
		self.page.write('setActivateMode("over");\n')
		self.page.write('}\n')

		self.page.write('}\n')
		
		self.page.write('</script>\n')
		
	def renderJavaScript(self):
		"""Render menu javascript.
		
		If alternate menu is used the menu is rendered using the JsMenu javascript menu,
		otherwise the the transmenu javascript menu is rendered."""
		
		if self.alternateMenu:
			self.renderJsMenuBarFunc()
			self.page.write(jsmenubarMenuInitTemplate % (self.scriptDir, self.scriptDir, self.scriptDir))
		else:
			self.page.write(transMenuInitTemplateStart % self.scriptDir)
			
			for menu in self.menus:
				self.page.write("""\t\tvar%s.onactivate = function() { document.getElementById("%s").className='hover'; };\n""" % (menu.getName(), menu.getName()))
				self.page.write("""\t\tvar%s.ondeactivate = function() { document.getElementById("%s").className='';};\n""" % (menu.getName(), menu.getName()))
				
			self.page.write(transMenuInitTemplateEnd)
		
	def renderBodyJavaScript(self):
		"""Render body menu javascript (override).
		
		If alternate menu is used the menu is rendered using the JsMenu javascript menu,
		otherwise the the transmenu javascript menu is rendered."""
		
		w = self.page.write
		
		if self.alternateMenu:
			pass
		else:
		
			w(transMenuDeclarationStart)
			
			for menu in self.menus:
				menu.renderJavaScript()	
				
			w(transMenuDeclarationEnd)					
	
	def render(self):
		"""Render the menu on the page."""
		
		if self.alternateMenu:
			positionStyleString = "position:absolute;left:%dpx;top:%dpx;" % (self.left, self.top-2)
			if self.fullWidth:
				positionStyleString = positionStyleString+"width:100%;"
			else:
				positionStyleString = positionStyleString+"width:%d" % self.width

			#self.page.writeln('<DIV id="jsmenu" style="%s"></DIV>' % positionStyleString)
		else:
		
			positionStyleString = "position:absolute;left:%dpx;top:%dpx;" % (self.left, self.top)
			
			if self.fullWidth:
				divMenu = DIV(id="menu", style=positionStyleString+"width:100%;")
			else:
				divMenu = DIV(id="menu", style=positionStyleString+"width:%d" % self.width)
				
			for menu in self.menus:
				
				if not menu.isSeparator():
					
					if menu.getSize()>0:
					
						divMenu.append(
							A(
								menu.getCaption(),
								id=menu.getName(),
								href="#",
								title=menu.getHint()
							 )
						)
						
					else:
						
						divMenu.append(
							A(
								menu.getCaption(),
								id=menu.getName(),
								href=menu.getLink(),
								title=menu.getHint(),
							 )
						)
	
				else:
					divMenu.append(HR(size=1,noshade=0))
					divMenu.append("&nbsp;")
			
			self.page.write(divMenu)
		
	
class Stack:
	"""Stack class.
	
	This class implements the classic stack data structure using
	a python list."""
	def __init__(self):
		"""Class constructor."""
		self.items = []

	def push(self, item):
		"""Push item onto the stack."""
		self.items.append(item)

	def pop(self):
		"""Pop item from the stack."""
		return self.items.pop()
	
	def current(self):
		"""Return current item on the stack."""
		return self.items[len(self.items)-1]
	
	def isEmpty(self):
		"""Returns True if stack is empty."""
		return(self.items == [])

class Form(FieldValidationMixin):
	"""Form class
	
	The form class implements a complete HTML input form that can be
	rendered on a WebKit page."""
	def __init__(self, name, action, caption="Noname", width=""):
		"""Class constructor
		
		@param name: form name
		@param action: The WebKit action associated with the form.
		@param caption: The form caption text.
		@param width: Form width string."""
		
		self._caption = caption
		self._action = action
		self._name = name
		
		self._width = width
		
		self._submitButtonName = "_action_submit"
		self._submitButtonValue = "Submit"
		
		self._controls = []
		self._buttons = []
		self._controlHelp = {}
		self._haveSubmit = True
		self._haveReset = False
		self._haveButtonRow = True
		self._defaultLabelWidth = "8em"
		self._defaultTextWidth = "8em"
		self._currentUnit = ""
		self._currentUnitWidth = 5
		
		self._fieldValues = {}
		self._fieldTypes = {}
		self._fileTransferFields = []
		
		self._haveNext = False
		self._havePrev = False
		
	def retrieveFieldValues(self, request):
		"""Retrieves field values from form request. Returns a dictionary
		containing the retrieved field values."""
		
		requestFields = request.fields()
		
		for fieldName in self._fieldValues.keys():
			fieldType = self._fieldTypes[fieldName]
			
			if fieldType == "string":
				self._fieldValues[fieldName] = self.getString(request, fieldName)
				
			if fieldType == "hostname":
				value = self.getHostname(request, fieldName)
				if value!=None:
					self._fieldValues[fieldName] = value

			if fieldType == "url":
				value = self.getURLString(request, fieldName)
				if value!=None:
					self._fieldValues[fieldName] = value

			if fieldType == "email":
				value = self.getURLString(request, fieldName)
				if value!=None:
					self._fieldValues[fieldName] = value

			if fieldType == "int":
				value = self.getInt(request, fieldName)
				print "fieldType int ", value
				if value!=None:
					self._fieldValues[fieldName] = value

			if fieldType == "float":
				value = self.getFloat(request, fieldName)
				if value!=None:
					self._fieldValues[fieldName] = value

			if fieldType == "password":
				value = self.getString(request, fieldName)
				if value!=None:
					self._fieldValues[fieldName] = value
				
			if fieldType == "checkbox":
				if requestFields.has_key(fieldName):
					self._fieldValues[fieldName] = True
				else:
					self._fieldValues[fieldName] = False

			if fieldType == "radio":
				if self.getString(request, fieldName)!=None:
					self._fieldValues[fieldName] = self.getString(request, fieldName)
				else:
					self._fieldValues[fieldName] = ""
	
		print self._fieldValues
		
	def getFieldValues(self):
		"""Return the field value dictionary.
		
		Contains the values retrieved using the retrieveFieldValues() method."""
		return self._fieldValues
	
	def getFieldTypes(self):
		"""Return the field type dictionary.
		
		Contains the field value types for the different fields in the form."""
		return self._fieldTypes
	
	def getFileTransferFields(self):
		"""Returns the names of the file transfer fields in the form."""
		return self._fileTransferFields
	
	def getName(self):
		"""Return form name."""
		return self._name
		
	def getWidth(self):
		"""Return form width string."""
		return self._width
		
	def beginFieldSet(self, legend, align=""):
		"""Begins a field set, that is a framed set of controls with a legend."""
		controlParams = (legend, "beginfieldset", align, "", "")
		self._controls.append(controlParams)
		
	def endFieldSet(self):
		"""Ends a field set."""
		controlParams = ("", "endfieldset", "", "", "")
		self._controls.append(controlParams)
		
	def beginIndent(self, width):
		"""Begin an indented set of controls."""
		controlParams = ("", "beginindent", "", width)
		self._controls.append(controlParams)
		
	def endIndent(self):
		"""End a set of indented controls."""
		controlParams = ("", "endindent", "", "", "")
		self._controls.append(controlParams)

	def beginSelect(self, label, name, size=4, multiple=False, width="10em", labelWidth=""):
		"""Begin a selection control."""
		if labelWidth == "":
			labelWidth = self._defaultLabelWidth		
		
		controlParams = (label, "beginselect", name, "", size, multiple, width, labelWidth)
		self._controls.append(controlParams)
		self._fieldValues[name] = ""
		self._fieldTypes[name] = "string"
		
	def addSpacer(self, width="4em", height="0em"):
		"""Add a spacer control."""
		controlParams = ("", "spacer", "", width, height, "")
		self._controls.append(controlParams)
			
	def addOption(self, value="Empty", selected=False):
		"""Add an option to a select control."""
		controlParams = ("", "option", "", value, selected, "")
		self._controls.append(controlParams)
	
	def endSelect(self):
		"""End select control."""
		controlParams = ("", "endselect", "", "", "", "")
		self._controls.append(controlParams)
		
	def addButton(self, label, name, width=""):
		"""Add a button control."""
		controlParams = (label, "button", name, width, "")
		self._controls.append(controlParams)

	def addSubmitButton(self, label, name, width=""):
		"""Add a submit button."""
		controlParams = (label, "submit", name, width, "")
		self._controls.append(controlParams)

	def addBreak(self):
		"""Add a break."""
		controlParams = ("", "break", "", "", "", "")
		self._controls.append(controlParams)
		
	def addSpacer(self, width = "8px", height = "1px"):
		"""Add a spacer."""
		controlParams = ("", "spacing", "", width, height)
		self._controls.append(controlParams)
		
	def setUnit(self, unit):
		"""Set current unit used in the text input controls."""
		self._currentUnit = unit
		
	def addText(self, label, name, value = "", width="", labelWidth="", fieldType="string"):
		"""Add text control."""
		if width == "":
			width = self._defaultTextWidth
		if labelWidth == "":
			labelWidth = self._defaultLabelWidth
			
		controlParams = (label, "text", name, value, "", width, labelWidth, self._currentUnit, self._currentUnitWidth)
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = fieldType
		
	def addTextArea(self, label, name, value = "", rows = 4, cols=20, labelWidth="", fieldType="string"):
		"""Add text area control."""
		if labelWidth == "":
			labelWidth = self._defaultLabelWidth
			
		controlParams = (label, "textarea", name, value, "", rows, cols, labelWidth, self._currentUnit)
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = fieldType
	
	def addPassword(self, label, name, value = ""):
		"""Add password control."""
		controlParams = (label, "password", name, value, "", "")
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = "password"
	
	def addReadonlyText(self, label, name, value = "", width="", labelWidth="", fieldType="string"):
		"""Add readonly text control."""
		if width == "":
			width = self._defaultTextWidth
		if labelWidth == "":
			labelWidth = self._defaultLabelWidth
		controlParams = (label, "text", name, value, "readonly", width, labelWidth, "")
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = "string"

	def addHidden(self, label, name, value = ""):
		"""Add hidden control."""
		controlParams = (label, "hidden", name, value, "", "")
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = "string"
	
	def addCheck(self, label, name, checked=False):
		"""Add checkbox control."""
		controlParams = (label, "checkbox", name, checked, "", "")
		self._controls.append(controlParams)
		self._fieldValues[name] = checked
		self._fieldTypes[name] = "checkbox"

	def addRadio(self, label, name, value=""):
		"""Add a radiobutton."""
		controlParams = (label, "radio", name, value, "")
		self._controls.append(controlParams)
		self._fieldValues[name] = value
		self._fieldTypes[name] = "radio"
	
	def addFile(self, label, name, value="", width="", labelWidth=""):
		"""Add a file control."""
		if width == "":
			width = self._defaultTextWidth
		if labelWidth == "":
			labelWidth = self._defaultLabelWidth
		controlParams = (label, "file", name, "", "", width, labelWidth)
		self._controls.append(controlParams)
		if name == "":
			self._fileTransferFields.append("fileUpload")
		else:
			self._fileTransferFields.append(name)
			
	def addNormalText(self, label):
		"""Add static text control."""
		controlParams = (label, "plaintext", "", "", "")
		self._controls.append(controlParams)

	def addSeparator(self):
		"""Add a separator."""
		self._controls.append(("", "-", "", "", ""))
		
	def setControlHelp(self, name, text, width = 200):
		"""Set control help."""
		self._controlHelp[name] = (text, width)

	def setAction(self, action):
		"""Set form action."""
		self._action = action

	def setName(self, name):
		"""Set form name."""
		self._name = name
		
	def addFormButton(self, label, name = ""):
		"""Add button to the bottom of the form."""
		self._buttons.append((label, name))
		
	def addFormButtonSpacer(self, width = "8px", height="1px"):
		"""Add spacer to bottom row of form buttons."""
		self._buttons.append(("", "spacer", width, height))

	def setSubmitButton(self, name, value):
		"""Set name and value of submit button."""
		self._submitButtonName = name
		self._submitButtonValue = value
		
	def setHaveSubmit(self, flag):
		"""If set to True the form has a standard submit button."""
		self._haveSubmit = flag
		
	def setHaveReset(self, flag):
		"""If set to True the form has a standard reset button."""		
		self._haveReset = flag
		
	def setHaveButtonRow(self, flag):
		"""If set to True the form will render a special button row at the
		bottom of the form."""		
		self._haveButtonRow = flag
		
	def setDefaultLabelWidth(self, width):
		"""Set the default label width string."""
		self._defaultLabelWidth = width
		
	def resetDefaultLabelWidth(self):
		"""Reset the default label width to the default value (8em)."""
		self._defaultLabelWidth = "8em"

	def setDefaultTextWidth(self, width):
		"""Set the default text width."""
		self._defaultTextWidth = width
		
	def resetDefaultTextWidth(self):
		"""Reset the default text width (8em)."""
		self._defaultLabelWidth = "8em"

	def setHaveGuideButtons(self, prev, next):
		"""Enable, disable special guide buttons on the form."""
		self._haveNext = next
		self._havePrev = prev
		
	def setDefaultUnitWidth(self, width):
		"""Set the default width of the unit area."""
		self._currentUnitWidth = width
		
	def resetDefaultUnitWidth(self):
		"""Reset the default width of the unit area (5)."""
		self._currentUnitWidth = 5

	def render(self, page):
		"""Render the form on a WebKit page."""
		
		if self._width=="":
			window = DIV(klass="lapWindow")
		else:
			window = DIV(klass="lapWindow", style="width: %s;" % self._width)
			
		windowHead = DIV(H2(self._caption),klass="lapWindowHead")
		window.append(windowHead)
		windowBody = DIV(klass="lapWindowBody")
		window.append(windowBody)
		
		form = FORM(method="Post", enctype="multipart/form-data", action=self._action)
			
		windowBody.append(form)
		
		currentFieldSet = form
		fieldSetStack = Stack()
		fieldSetStack.push(form)
		
		currentSelect = None
				
		for control in self._controls:
			if control[1]<>"-":
				if control[1]<>"hidden":
					
					if self._controlHelp.has_key(control[2]):
						mouseOver = "ddrivetip('%s', %d)" % (self._controlHelp[control[2]][0], self._controlHelp[control[2]][1])
						mouseOut = "hideddrivetip()"
					else:
						mouseOver = "ddrivetip('No help exits.', 150)" 
						mouseOut = "hideddrivetip()"
					
					if control[1]=="break":
						currentFieldSet.append(BR())
					elif control[1]=="spacer":
						currentFieldSet.append(IMG(src="images/trans.gif", width=control[3], height=control[4]))
					elif control[1]=="beginindent":
						newFieldSet = DIV(style="text-indent:%s;" % control[3])
						fieldSetStack.push(newFieldSet)
						currentFieldSet.append(newFieldSet)
						currentFieldSet = newFieldSet
					elif control[1]=="endindent":
						fieldSetStack.pop()
						currentFieldSet = fieldSetStack.current()
					elif control[1]=="beginfieldset":
						if control[2]=="":
							newFieldSet = FIELDSET(LEGEND(control[0]))
						else:
							newFieldSet = FIELDSET(LEGEND(control[0]), style="float: %s;" % control[2])
						fieldSetStack.push(newFieldSet)
						currentFieldSet.append(newFieldSet)
						currentFieldSet = newFieldSet
					elif control[1]=="endfieldset":
						fieldSetStack.pop()
						currentFieldSet = fieldSetStack.current()
					elif control[1]=="beginselect":
						# ("", "beginselect", name, "", size, multiple)

						if control[5]==True:
							currentSelect = SELECT(name=control[2], size=control[4], multiple=True, style="width: %s;" % control[6])
						else:
							currentSelect = SELECT(name=control[2], size=control[4], style="width: %s;" % control[6])
						
						currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s;" % control[7], onmouseover=mouseOver, onmouseout=mouseOut))
						
						currentFieldSet.append(currentSelect)
							
					elif control[1]=="endselect":
						currentSelect = None
					elif control[1]=="option":
						# ("", "option", "", value, selected)
						if currentSelect!=None:
							if control[4]==True:
								currentSelect.append(OPTION(control[3], value=control[3], selected=True))
							else:
								currentSelect.append(OPTION(control[3], value=control[3]))
					elif control[1]=="radio":
						currentFieldSet.append(LABEL(control[0], label_for=control[2]))
						currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3]))
					elif control[1]=="checkbox":
						currentFieldSet.append(LABEL(control[0], label_for=control[2]))
						currentFieldSet.append(INPUT(type=control[1], name=control[2], checked=control[3]))
					elif control[1]=="plaintext":
						currentFieldSet.append(P(control[0]))
						#currentFieldSet.append(LABEL(control[0], label_for=control[2]))
						#currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3]))
					elif control[1]=="button":
						if control[3]=="":
							currentFieldSet.append(INPUT(type=control[1], value=control[0], name=control[2]))
						else:
							currentFieldSet.append(INPUT(type=control[1], value=control[0], name=control[2], style="width: %s;" % control[3]))						
					elif control[1]=="submit":
						if control[3]=="":
							currentFieldSet.append(INPUT(type=control[1], value=control[0], name=control[2]))
						else:
							currentFieldSet.append(INPUT(type=control[1], value=control[0], name=control[2], style="width: %s;" % control[3]))
					elif control[1]=="text":
												
						if control[5]!="":
							width = control[5]
							
						if control[6]!="":
							labelWidth = control[6]
							
						if control[4]=="":
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3], style="width: %s" % width))
							if control[7]!="":
								currentFieldSet.append(INPUT(type="input", value=control[7], style="padding-left: 0.5em; border: 1px; background-color: transparent;", readonly=1, border=1, size=control[8]))
						else:
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3], readonly=1, style="width: %s" % width))						
							if control[7]!="":
								currentFieldSet.append(INPUT(type="input", value=control[7], style="border: 1px; background-color: transparent;", readonly=1, border=1, size=control[8]))
					elif control[1]=="textarea":
						
						textRows = control[5]
						textCols = control[6]
						
						if control[7]!="":
							labelWidth = control[7]
							
						if control[4]=="":
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(TEXTAREA(name=control[2], rows=textRows, cols=textCols))
						else:
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(TEXTAREA(name=control[2], readonly=1, rows=textRows, cols=textCols))						
						
					else:

						if control[5]!="":
							width = control[5]
							
						if control[6]!="":
							labelWidth = control[6]

						if control[4]=="":
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3], style="width: %s" % width))
						else:
							currentFieldSet.append(LABEL(control[0], label_for=control[2], style="width: %s" % labelWidth, onmouseover=mouseOver, onmouseout=mouseOut))
							currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3], readonly=1, style="width: %s" % width))						
				else:
					currentFieldSet.append(INPUT(type=control[1], name=control[2], value=control[3]))
						
			else:
				currentFieldSet.append(HR(), BR())
		
		form.append(BR())
		
		if self._haveButtonRow:
			
			buttonTable = TABLE(width="100%", border = "0px")
			buttonTableRow = TR()
			buttonLeftCell = TD(width="60")
			buttonMiddleCell = TD()
			buttonRightCell = TD(align="right", width="60")
			
			buttonTableRow.append(buttonLeftCell)
			buttonTableRow.append(buttonMiddleCell)
			buttonTableRow.append(buttonRightCell)
			
			buttonTable.append(buttonTableRow)
			
			buttonRow = CENTER()
			
			buttonMiddleCell.append(buttonRow)
			
			if self._havePrev:
				buttonLeftCell.append(INPUT(type="submit", name="_action_formPrev", value="Prev"))
			
			if self._haveNext:
				buttonRightCell.append(INPUT(type="submit", name="_action_formNext", value="Next"))

			form.append(buttonTable)
							
			for button in self._buttons:
				if len(button)==2:
					buttonRow.append(INPUT(type="submit", name=button[1], value=button[0]))
				else:
					buttonRow.append(IMG(src="images/trans.gif", width=button[2], height=button[3]))
			if self._haveSubmit:
				buttonRow.append(INPUT(type="submit", name=self._submitButtonName, value=self._submitButtonValue))
	
			if self._haveReset:	
				buttonRow.append(INPUT(type="reset", name="btnReset", value = "Reset"))			
			
		page.write(window)
	
class TableForm:
	"""Form class
	
	The TableForm class implements a complete table based HTML input form that can be
	rendered on a WebKit page."""	
	def __init__(self, name, action, caption="Noname", width="50em", rows=5, cols=5, contentID="formContent"):
		self._caption = caption
		self._width = width
		self._action = action
		self._name = name
		self._submitButtonName = "_action_submit"
		self._submitButtonValue = "Submit"
		self._controls = []
		self._buttons = []
		self._haveSubmit = True
		self._haveButtons = True
		
		self._solidColor = False
		
		self.setTableSize(rows, cols)
		
	def setHaveButtons(self, flag):
		"""Determines if default buttons are rendered."""
		self._haveButtons = flag
		
	def getHaveButtons(self):
		"""Return True if default buttons are rendered."""
		return self._haveButtons
		
	def setSolidColor(self, flag):
		"""Determines if a solid color should be used for the
		entire form. The default (True) mode is to render rows
		alternating between 2 colors."""
		self._solidColor = flag
				
	def getSolidColor(self):
		"""Return true if a solid color is used on the entire
		form. Otherwise (default) an alternating color scheme is
		used."""
		return self._solidColor
				
	def setTableSize(self, rows, cols):
		"""Set the size of the table used in the form."""
		self._table = []
		self._tableColors = []
		self._tableControls = []
		
		self._rows = rows
		self._cols = cols
		
		for r in range(0,rows):
			self._table.append([])
			self._tableColors.append([])
			self._tableControls.append([])
			for c in range(0,cols):
				self._table[r].append("")
				self._tableColors[r].append("")
				self._tableControls[r].append(None)

	def addText(self, label, name, value = "", row=-1, col=-1):
		"""Add a text control to the form."""
		controlParams = (label, "text", name, value, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addPassword(self, label, name, value = "", row=-1, col=-1):
		"""Add a password control to the form."""
		controlParams = (label, "password", name, value, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addReadonlyText(self, label, name, value = "", row=-1, col=-1):
		"""Add a readonly text control to the form."""
		controlParams = (label, "text", name, value, "readonly")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addHidden(self, label, name, value = "", row=-1, col=-1):
		"""Add a hidden text control to the form."""
		controlParams = (label, "hidden", name, value, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addButton(self, label, name, row=-1, col=-1):
		"""Add a button to the form."""
		controlParams = (label, "button", name, label, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addCheck(self, label, name, checked=False, row=-1, col=-1):
		"""Add a checkbox to the form."""
		controlParams = (label, "checkbox", name, checked, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addRadio(self, label, name, value="", row=-1, col=-1):
		"""Add a radiobutton to the form.
		
		For the radiobuttons to work, they require that
		the same name is used for each selection group."""
		controlParams = (label, "radio", name, value, "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addFile(self, label, name, value="", row=-1, col=-1):
		"""Add a file upload control."""
		controlParams = (label, "file", name, "", "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams
			
	def addNormalText(self, label, row = -1, col=-1):
		"""Add static text to the form."""
		controlParams = (label, "plaintext", "", "", "")
		self._controls.append(controlParams)
		if row>=0:
			self._tableControls[row][col] = controlParams

	def addSeparator(self):
		"""Add separator."""
		self._controls.append(("", "-", "", "", ""))

	def setAction(self, action):
		"""Set the name of the action used for responding to a form
		POST action."""
		self._action = action

	def setName(self, name):
		"""Set form name."""
		self._name = name
		
	def addFormButton(self, label, name = ""):
		"""Add special buttons to the bottom part of the form."""
		self._buttons.append((label, name))
		
	def addFormSpacer(self, width = "8px", height = "1px"):
		"""Add a form spacer.
		
		This control can be used to expand table cell to a specific
		width or height."""
		self._buttons.append(("", "spacer", width, height))

	def setSubmitButton(self, name, value):
		"""Set the name and value of the form submit button."""
		self._submitButtonName = name
		self._submitButtonValue = value
		
	def setHaveSubmit(self, flag):
		"""Return True if the form has a submit button."""
		self._haveSubmit = flag
		
	def render(self, page):
		"""Render the form to a WebKit Page."""
		
		if self._width=="":
			window = DIV(klass="lapWindow")
		else:
			window = DIV(klass="lapWindow", style="width: %s;" % self._width)
			
		windowHead = DIV(H2(self._caption),klass="lapWindowHead")
		window.append(windowHead)
		windowBody = DIV(klass="lapWindowBody")
		window.append(windowBody)
		
		form = FORM(method="Post", enctype="multipart/form-data", action=self._action)
			
		windowBody.append(form)

		table = TABLE(klass="lapFormTable")
		
		form.append(table)
				
		cellID    = "cellStyle1"
		cellIDAlt = "cellStyle2"

		row = 0
		col = 0
		
		AltColor = False
		
		while row<self._rows:
			
			tableRow = TR()
			table.append(tableRow)
			while col<self._cols:
				
				control = self._tableControls[row][col]
				
				if not self._solidColor:
					if AltColor:
						currentID = cellID
					else:
						currentID = cellIDAlt
				else:
					currentID = cellID
				
				if control!=None:
					if control[1]<>"hidden":
						if control[1]=="radio":
							tableRow.append(
									TD(INPUT(type=control[1], name=control[2], value=control[3]), id=currentID)
							)
						elif control[1]=="checkbox":
							tableRow.append(
									TD(INPUT(type=control[1], name=control[2], value=control[3], checked=False), id=currentID)
							)
						elif control[1]=="plaintext":
							tableRow.append(
									TD(control[0], id=currentID)
							)
						else:
							if control[4]=="":
								tableRow.append(
										TD(INPUT(type=control[1], name=control[2], value=control[3]))
								)
							else:
								tableRow.append(
										TD(INPUT(
											type=control[1],
											name=control[2],
											value=control[3],
											readonly=1
											), id=currentID
										)
								)
					else:
						table.append(INPUT(type=control[1], name=control[2], value=control[3]))
				else:
					table.append(TD(id=currentID))
										
				col = col + 1
						
			col = 0
			row = row + 1
			AltColor = not AltColor
				

		if self._haveButtons:

			buttonRow = TR()
			buttonData = TD(colspan=self._cols, style="text-align: center")
				
			buttonRow.append(buttonData)
			table.append(buttonRow)
			
			for button in self._buttons:
				if len(button)==2:
					buttonData.append(INPUT(type="submit", name=button[1], value=button[0]))
				else:
					buttonData.append(IMG(src="images/trans.gif", width=button[2], height=button[3]))
			if self._haveSubmit:
				buttonData.append(INPUT(type="submit", name=self._submitButtonName, value=self._submitButtonValue))

		page.write(window)

class Window:
	"""Render a generic window."""
	def __init__(self, caption="Window", width="30em"):
		self._caption = caption
		self._width = width
		self._content = None
		self._body = DIV(klass="lapWindowBody")

	def setContent(self, content):
		"""Set the content inside the window (string)."""
		self._content = content
		
	def getBody(self):
		"""Return the body of the Window as a HyperText instance."""
		return self._body
			
	def render(self, page):
		"""Render the window to a WebKit Page instance."""
		if self._width=="":
			window = DIV(klass="lapWindow")
		else:
			window = DIV(klass="lapWindow", style="width: %s;" % self._width)
			
		windowHead = DIV(H2(self._caption),klass="lapWindowHead")
		window.append(windowHead)
		window.append(self._body)
		
		page.write(window)
	
