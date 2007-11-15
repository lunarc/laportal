#
# VOPage base class module
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

"""VOPage class module"""

from Web.ApplicationPage import ApplicationPage
from time import *

import os
import sys
import string
import pickle

import Lap
import Lap.Session

import Web
import Web.Ui
import Web.UiExt
import Web.Dialogs

class MenuTestPage(ApplicationPage):
	"""VOPage base class
	
	This base class is the base for any VO plugins. The class implements
	a generic VO joining request."""
	
	# ----------------------------------------------------------------------
	# Private methods
	# ----------------------------------------------------------------------	

	# ----------------------------------------------------------------------
	# Get/set methods
	# ----------------------------------------------------------------------
	
	def setReturnPage(self, returnPage):
		adapterName = self.request().adapterName()
		self._returnPage = "%s/context/" % returnPage
		
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			

	def onInit(self, adapterName):
		
		form = Web.UiExt.Form(self, "testform")
		form.caption = "Testform"
		form.URL = "%s/context/MenuTestPage" % adapterName
		form.width = 500
		
		fieldSet = Web.UiExt.FieldSet(self)
		fieldSet.legend = "test"
		
		form.add(fieldSet)
		
		textField1 = Web.UiExt.TextField(self, 'textField1')
		textField1.fieldLabel = "Name"
		textField1.width = 175
		textField1.allowBlank = False

		fieldSet.add(textField1)
		
		textField2 = Web.UiExt.TextField(self, 'textField2')
		textField2.fieldLabel = "Address"
		textField2.width = 175
		textField2.allowBlank = False
		
		fieldSet.add(textField2)
		
		textField2 = Web.UiExt.NumberField(self, 'numberField')
		textField2.fieldLabel = "Number"
		textField2.width = 175
		textField2.allowBlank = False
		
		fieldSet.add(textField2)
		
		fieldSet2 = Web.UiExt.FieldSet(self)
		fieldSet2.legend = "test2"
		
		form.add(fieldSet2)

		comboBox = Web.UiExt.ComboBox(self, 'comboTest')
		comboBox.add("Hello", "hello")
		comboBox.add("Hello1", "hello1")
		comboBox.add("Hello2", "hello2")
		
		fieldSet2.add(comboBox)

		textArea = Web.UiExt.TextArea(self, 'textarea')
		textArea.value = ["hello, world!", "helloo..."]
		
		fieldSet2.add(textArea)
		
		fieldSet3 = Web.UiExt.FieldSet(self)
		fieldSet3.legend = "test3"
		
		form.add(fieldSet3)
		
		checkBox1 = Web.UiExt.CheckBox(self, 'checkBox1', 'checkBox1', 'value1', 'v1')
		checkBox1.value = True
		fieldSet3.add(checkBox1)

		checkBox2 = Web.UiExt.CheckBox(self, 'checkBox1', 'checkBox2', 'value2', 'v2')
		fieldSet3.add(checkBox2)

		checkBox3 = Web.UiExt.CheckBox(self, 'checkBox1', 'checkBox3', 'value3', 'v3')
		fieldSet3.add(checkBox3)

		fieldSet4 = Web.UiExt.FieldSet(self)
		fieldSet4.legend = "test4"
		
		form.add(fieldSet4)
		
		radio1 = Web.UiExt.Radio(self, 'radioTest4', 'radio1', 'value1', 'v1')
		radio1.value = True
		fieldSet4.add(radio1)

		radio2 = Web.UiExt.Radio(self, 'radioTest4', 'radio2', 'value2', 'v2')
		fieldSet4.add(radio2)

		radio3 = Web.UiExt.Radio(self, 'radioTest4', 'radio3', 'value3', 'v3')
		fieldSet4.add(radio3)

		fieldSet5 = Web.UiExt.FieldSet(self)
		fieldSet5.legend = "test5"
		
		form.add(fieldSet5)
		
		fileField = Web.UiExt.FileField(self, 'fileField')
		fileField.destinationDir = "d:\dev\local-webware"
		fieldSet5.add(fileField)
		
		buttonSet = Web.UiExt.ButtonSet(self, 'buttonSet')

		submitButton = Web.UiExt.Button(self, 'test', 'Submit')
		buttonSet.add(submitButton)

		hideButton = Web.UiExt.Button(self, 'hide', 'Hide')
		buttonSet.add(hideButton)
		
		form.add(buttonSet)

		otherForm = Web.UiExt.Form(self, "showhideForm")
		otherForm.caption = "Testform"
		otherForm.URL = "%s/context/MenuTestPage" % adapterName
		otherForm.width = "500px"
		otherForm.visible = False
		
		showButton = Web.UiExt.Button(self, 'show', 'Show')
		buttonSet2 = Web.UiExt.ButtonSet(self, 'buttonSet2')
		buttonSet2.add(showButton)
		otherForm.add(buttonSet2)
		
		self.addControl("form", form)
		self.addControl("otherForm", otherForm)
		
	def onUseMenu(self):
		return True

	# ----------------------------------------------------------------------
	# Form action methods
	# ----------------------------------------------------------------------
		
	def test(self):
		print "In test()"
		form = self.getExtControl("form")
		form.retrieve(self.request())
		form.values["numberField"] = 42.0
		form.values["textarea"] = ["row1", "row2"]
		print form.values
		form.update()
		self.redraw()
		
	def hide(self):
		print "hide()"
		form = self.getExtControl("form")
		form.visible = False
		
		otherForm = self.getExtControl("otherForm")
		otherForm.visible = True
		
		self.redraw()
		
	def show(self):
		print "show()"
		form = self.getExtControl("form")
		form.visible = True
		
		otherForm = self.getExtControl("otherForm")
		otherForm.visible = False
		
		self.redraw()
