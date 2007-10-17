#
# UiControls module
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

from HyperText.HTML import *

class FormControl:
	def __init__(self, name="", caption="", type="", fieldType="string"):
		self._name=name
		self._caption=caption
		self._type=type
		self._fieldType = "string"
		self._vtype = ""
		
	def setName(self, name):
		self._name = name
	
	def setCaption(self, caption):
		self._caption = caption
		
	def setType(self, type):
		self._type = type
		
	def setFieldType(self, fieldType):
		self._fieldType = fieldType
		
		if (self._fieldType=="string"):
			self._vtype = ""
		elif (self._fieldType=="hostname"):
			self._vtype = ""
		elif (self._fieldType=="url"):
			self._vtype = "url"
		elif (self._fieldType=="email"):
			self._vtype = "email"
		else:
			self._vtype = ""	
		
	def _render(self):
		return P()
	
	def render(self):
		if self._visible:
			tag = self._render()
			self._page.writeln(tag)
		else:
			self._page.writeln("")
			
	def _renderJS(self):
		return ""
	
	def renderJS(self):
		self._page.writeln(self._renderJS())
			
	def renderJSToString(self):
		return self._renderJS()
		
	def renderToString(self):
		tag = self._render()
		return tag.__str__()
	
	def renderToTag(self):
		return self._render()

class TextControl(FormControl):
	def __init__(self, name="", caption="", value="", size="", fieldType="string"):
		FormControl.__init__(self, name, caption, type="TEXT", fieldType=fieldType)
		self._value = value
		self._size = size
		
	def _render(self):
		formItem = DIV(klass="x-form-item")
		formElement = DIV(klass="x-form-element")
		formItem.append(LABEL(self._caption, label_for=self._name))
		if self._size=="":
			formElement.append(INPUT(type=self._type, name=self._name, value=self._value, id=self._name))
		else:
			formElement.append(INPUT(type=self._type, name=self._name, size=self._size, value=self._value, id=self._name))
			
		formItem.append(formElement)
		return formItem
	
	def _renderJS(self):
		
		options = ""
		
		if self._vtype != "":
			options += "vtype:'%s'" % self._vtype
		else:
			options = ""
		
		return "var %(name)s = new Ext.form.TextField({%(options)s});   %(name)s.applyTo('%(name)s');" % {'name':self._name, 'options':options}

			
class TextAreaControl(FormControl):
	def __init__(self, name="", caption="", value="", rows=4, cols=40, fieldType="string"):
		FormControl.__init__(self, name, caption, type="TEXTAREA", fieldType=fieldType)
		self._value = value
		self._rows = rows
		self._cols = cols
		
	def _render(self):
		formItem = DIV(klass="x-form-item")
		formElement = DIV(klass="x-form-element")
		formItem.append(LABEL(self._caption, label_for=self._name))
		textArea = TEXTAREA(name=self._name, rows=str(self._rows), cols=str(self._cols), id=self._name)
		textArea.append(self._value)
		formElement.append(textArea)
		formItem.append(formElement)
		return formItem
	
	def _renderJS(self):
		
		options = ""
		
		if self._vtype != "":
			options += "vtype:'%s'" % self._vtype
		else:
			options = ""
		
		return "var %(name)s = new Ext.form.TextArea({%(options)s});   %(name)s.applyTo('%(name)s');" % {'name':self._name, 'options':options}
	
class ButtonControl(FormControl):
	def __init__(self, name="", caption="", width=""):
		FormControl.__init__(self, name, caption, type="BUTTON")
		self._width = width
		
	def _render(self):
		formItem = DIV(klass="x-form-item")
		formElement = DIV(klass="x-form-element")
		formItem.append(LABEL(self._caption, label_for=self._name))
		if self._width=="":
			formElement.append(INPUT(type=self._type, name=self._name, value=self._caption, id=self._name))
		else:
			formElement.append(INPUT(type=self._type, name=self._name, value=self._caption, id=self._name, width=self._width))
		formItem.append(formElement)
		return formItem
	
	def _renderJS(self):
		
		options = ""
		
		if self._vtype != "":
			options += "vtype:'%s'" % self._vtype
		else:
			options = ""
		
		return "var %(name)s = new Ext.Button({%(options)s});   %(name)s.applyTo('%(name)s');" % {'name':self._name, 'options':options}
		
class ReadOnlyTextControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)
		
class PasswordControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)

class HiddenControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)
		
class CheckControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)
	
class RadioControl(FormControl):	
	def __init__(self):
		FormControl.__init__(self)

class SeparatorControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)
		
class FileControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)	

		
class GroupControl(FormControl):
	def __init__(self):
		FormControl.__init__(self)
	
class FieldSetControl(GroupControl):
	def __init__(self):
		FormControl.__init__(self)
	