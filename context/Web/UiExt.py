from HyperText.HTML import *
from Security import *

import sys, os

class Base(object):
	def __init__(self, page = None, name = "extbase"):
		self.__name = name
		self.__visible = True
		self.__page = page
		self.__id = name
		self.__actionEnabled = False
		self.__javascriptOutput = []
		
	def clearJavaScript(self):
		self.__javascriptOutput = []
		
	def addJS(self, jsLine):
		self.__javascriptOutput.append(jsLine)

	def setName(self, name):
		self.__name = name
		
	def getName(self):
		return self.__name
	
	def setVisible(self, visible):
		self.__visible = visible
		
	def getVisible(self):
		return self.__visible
	
	def setPage(self, page):
		self.__page = page
		
	def getPage(self):
		return self.__page
	
	def setId(self, id):
		self.__id = id
		
	def getId(self):
		return self.__id
	
	def getAction(self):
		return self.__name

	def getActionName(self):
		return "_action_"+self.__name

	def getActionEnabled(self):
		return self.__actionEnabled
	
	def setActionEnabled(self, flag):
		self.__actionEnabled = flag
		
	def hasActions(self):
		return False
	
	def doRender(self):
		return P()
	
	def render(self):
		if self.__visible:
			tag = self.doRender()
			self.__page.writeln(tag)
		else:
			self.__page.writeln("")
			
	def doSetupJavaScript(self):
		pass
	
	def renderJS(self):
		self.clearJavaScript()
		self.doSetupJavaScript(self)
		self.__page.writeln("\n".join(self.__javascriptOutput))
			
	def renderJSToString(self):
		self.clearJavaScript()
		self.doSetupJavaScript()
		return "\n".join(self.__javascriptOutput)
		
	def renderToString(self):
		tag = self.doRender()
		return tag.__str__()
	
	def renderToTag(self):
		if self.__visible:
			tag = self.doRender()
			return tag
		else:
			return None

	name = property(getName, setName)
	visible = property(getVisible, setVisible)
	page = property(getPage, setPage)
	id = property(getId, setId)
	action = property(getAction, None)
	actionName = property(getActionName, None)
	actionEnabled = property(getActionEnabled, setActionEnabled)
	
class Container(Base):
	def __init__(self, page=None, name="extcontainer"):
		Base.__init__(self, page, name)
		self.__extObjects = []
		self.__sysObjects = []
		
	def add(self, extObject):
		self.__extObjects.append(extObject)
		
	def addSystem(self, extObject):
		self.__sysObjects.append(extObject)
		
	def doSetupJavaScript(self):
		self.addJS("Ext.onReady(function(){")
		self.addJS("// System objects")
		for extObj in self.__sysObjects:
			self.addJS(extObj.renderJSToString())			
		self.addJS("// Controls")
		for extObj in self.__extObjects:
			self.addJS(extObj.renderJSToString())
		self.addJS("});")
		
	def doRender(self):
		tag = DIV()
		for extObj in self.__extObjects:
			extObj.page = self.page
			objTag = extObj.renderToTag()
			if objTag!=None:
				tag.append(extObj.renderToTag())
			
		return tag
	
	def getActions(self):
		
		actions = []
		
		for control in self.__extObjects:
			if control.hasActions():
				actions += control.actions
				
		return actions
	
	def getControlCount(self):
		return len(self.__extObjects)
	
	actions = property(getActions, None)
	controlCount = property(getControlCount, None)

class Form(Base):
	def __init__(self, page = None, name = "Form", renderTarget = "extform"):
		Base.__init__(self, page, name)
		self.__renderTarget = renderTarget
		self.__caption = "My form"
		self.__labelWidth = 75
		self.__url = ""
		self.__width = 400
		self.__sizeUnit = "px"
		self.__controls = []
		self.__actions = []
		self.__values = {}
		
	def clear(self):
		self.__controls = []
		self.__actions = []
		
	def add(self, control):
		if control.actionEnabled:
			self.__actions.append(control.action)
			
		if isinstance(control, ButtonSet):
			for button in control.controls:
				if button.actionEnabled:
					self.__actions.append(button.action)

		self.__controls.append(control)
		
	def setRenderTarget(self, target):
		self.__renderTarget = target

	def getRenderTarget(self):
		return self.__renderTarget
	
	def setCaption(self, caption):
		self.__caption = caption
		
	def getCaption(self):
		return self.__caption
	
	def setLabelWidth(self, width):
		self.__labelWidth = width
		
	def getLabelWidth(self):
		return self.__labelWidth
	
	def setURL(self, url):
		self.__url = url
		
	def getURL(self):
		return self.__url
	
	def setWidth(self, width):
		self.__width = width
		
	def getWidth(self):
		return self.__width
	
	def setSizeUnit(self, sizeUnit):
		self.__sizeUnit = sizeUnit
		
	def getSizeUnit(self):
		return self.__sizeUnit
	
	def getActions(self):
		return self.__actions
	
	def hasActions(self):
		return True
	
	def getValues(self):
		return self.__values
	
	def recRetrieve(self, request):
		
		controlValues = {}
		
		for control in self.__controls:

			if isinstance(control, Field):
				control.retrieve(request)
				if not controlValues.has_key(control.name):
					controlValues[control.name] = control.value

			if isinstance(control, FieldSet):
				setValues = control.recRetrieve(request)
				
				for valueName in setValues.keys():
					if not controlValues.has_key(valueName):
						controlValues[valueName] = setValues[valueName]
				
		return controlValues
	
	def retrieve(self, request):
		self.__values = self.recRetrieve(request)
		
	def recUpdate(self, formDict):
		for control in self.__controls:
			if isinstance(control, Field):
				control.update(formDict)
			if isinstance(control, FieldSet):
				control.update(formDict)
		
	def update(self):
		self.recUpdate(self.__values)	
	
	def doSetupJavaScript(self):
		
		# Initialise form
		
		if len(self.__controls)>0:
			for formControl in self.__controls:
				self.addJS(formControl.renderJSToString())
					
	def doRender(self):
		form = FORM(id=self.name, klass="x-form", action=self.URL, method="POST", enctype="multipart/form-data")

		#position:absolute;
		#top: 50%;
		#left: 50%;
		#width:30em;
		#height:18em;
		#margin-top: -9em; /*set to a negative number 1/2 of your height*/
		#margin-left: -15em; /*set to a negative number 1/2 of your width*/
		
		formOuter = DIV(style="width:%d%s;position: absolute;left:50%%;margin-left: -%d%s;" % (self.__width, self.__sizeUnit, self.__width/2, self.__sizeUnit))
		form.append(formOuter)
		formOuter.append(DIV(DIV(DIV(klass="x-box-tc"),klass="x-box-tr"),klass="x-box-tl"))
		formInner = DIV(klass="x-box-mc")
		formDecoration =  DIV(DIV(formInner,klass="x-box-mr"),klass="x-box-ml")
		formOuter.append(formDecoration)
		formInner.append(H3(self.caption))
		formLayout = DIV(id="container", klass="x-form-bd")
		formInner.append(formLayout)
		
		for formControl in self.__controls:
			formLayout.append(formControl.renderToTag())
			
		formOuter.append((DIV(DIV(DIV(klass="x-box-bc"),klass="x-box-br"),klass="x-box-bl")))
		
		return form
	
	renderTarget = property(getRenderTarget, setRenderTarget)
	caption = property(getCaption, setCaption)
	labelWidth = property(getLabelWidth, setLabelWidth)
	URL = property(getURL, setURL)
	width = property(getWidth, setWidth)
	sizeUnit = property(getSizeUnit, setSizeUnit)
	actions = property(getActions, None)
	values = property(getValues, None)
	
class Field(Base, FieldValidationMixin):
	def __init__(self, page=None, name = "field"):
		Base.__init__(self, page, name)
		
		self.__fieldType = "string"
		self.__value = ""
		
	def setFieldType(self, fieldType):
		self.__fieldType = fieldType
		
	def getFieldType(self):
		return self.__fieldType
	
	def setValue(self, value):
		self.__value = value
		
	def getValue(self):
		return self.__value
	
	def retrieve(self, request):
		if self.fieldType == "float":
			self.value = self.getFloat(request, self.name)
		if self.fieldType == "int":
			self.value = self.getInt(request, self.name)
		if self.fieldType == "string":
			self.value = self.getString(request, self.name)
		if self.fieldType == "multistring":
			self.value = self.getMultiString(request, self.name)
		if self.fieldType == "hostname":
			self.value = self.getHostname(request, self.name)
		if self.fieldType == "url":
			self.value = self.getURLField(request, self.name)
		if self.fieldType == "email":
			self.value = self.getEmail(request, self.name)
			
	def update(self, formDict):
		if formDict.has_key(self.name):
			self.value = formDict[self.name]
	
	fieldType = property(getFieldType, setFieldType)
	value = property(getValue, setValue)
	
class Hidden(Field):
	def __init__(self, page=None, name = "hiddenfield"):
		Field.__init__(self, page, name)
		
	def doRender(self):
		input = INPUT(type="hidden", name=self.name, id=self.name, value=str(self.value))
		return input
	
class FileField(Field):
	def __init__(self, page=None, name = "filefield", fieldLabel = "FileField", width = 175, allowBlank = True):
		Field.__init__(self, page, name)
		self.__fieldLabel = fieldLabel
		self.__destDir = ""
		self.__filename = ""
		self.__uploadStatus = False
		self.fieldType = "file"
		
	def doSetupJavaScript(self):
		pass
	
	def doRender(self):
		item = DIV(klass="x-form-item")
		label = LABEL(self.fieldLabel, label_for=self.name)
		item.append(label)
		element = DIV(klass="x-form-element")
		item.append(element)
		input = INPUT(type="file", name=self.name, id=self.name, value=str(self.value))
		item.append(input)
		return item
		
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
	
	def setDestDir(self, destDir):
		self.__destDir = destDir
		
	def getDestDir(self):
		return self.__destDir
	
	def setFilename(self, filename):
		self.__filename = filename
		
	def getFilename(self):
		return self.__filename
	
	def getUploadStatus(self):
		return self.__uploadStatus
	
	def retrieve(self, request):
		"""Handles a HTTP file upload request from the
		request file, fieldName, and copies it to the directory
		specified by destDir."""
		
		self.__uploadStatus = False
		
		print "retrieve()"
		
		if request.hasField(self.name):
			
			print "retrieve has file field."

			filename = ""

			self.__uploadStatus = True
			try:
				print "Try upload."
				f = request.field(self.name)
				print "f =",f
				fileContent = f.file.read()
				
				
				if f.filename.find("\\")!=-1:
					print "explorer upload..."
					#lapDebug("Explorer upload...")
					
					lastBackslash = f.filename.rfind("\\")
					self.__filename = f.filename[lastBackslash+1:]
					#lapDebug("modified filename = " + self.__filename)
				else:
					print "normal upload..."
					print "f.filename =", f.filename
					self.__filename = f.filename
					
				#lapDebug("Upload filename = " + self.__filename)
				print "upload filename", self.__filename
				print "destination dir", self.__destDir
				inputFile = file(os.path.join(self.__destDir, self.__filename), "w")
				inputFile.write(fileContent)
				inputFile.close()
			except:
				print "Unexpected error:", sys.exc_info()[0]
				self.__uploadStatus = False
				return
			
			if self.__uploadStatus:
				#lapInfo("File, %s, uploaded to %s." % (self.__filename, self.__destDir))
				return 
			else:
				return 
			
		else:
			return

				
	fieldLabel = property(getFieldLabel, setFieldLabel)
	destinationDir = property(getDestDir, setDestDir)
	filename = property(getFilename, setFilename)
	uploadStatus = property(getUploadStatus, None)
	
class TextField(Field):
	def __init__(self, page=None, name = "textfield", fieldLabel = "Textfield", width = 175, allowBlank = True):
		Field.__init__(self, page, name)
		self.__fieldLabel = fieldLabel
		self.__width = width
		self.__allowBlank = allowBlank
		self.fieldType = "string"
		
	def doSetupJavaScript(self):
		flagString = "true"
		if not self.__allowBlank:
			flagString = "false"
		self.addJS("var %s = new Ext.form.TextField({applyTo: '%s', fieldLabel: '%s', name: '%s', width: %d, allowBlank: %s});" % (self.name, self.name, self.__fieldLabel, self.name, self.__width, flagString))
	
	def doRender(self):
		item = DIV(klass="x-form-item")
		label = LABEL(self.fieldLabel, label_for=self.name)
		item.append(label)
		element = DIV(klass="x-form-element")
		item.append(element)
		input = INPUT(type="text", name=self.name, id=self.name, value=str(self.value))
		item.append(input)
		return item
		
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
		
	def setWidth(self, width):
		self.__width = width
		
	def getWidth(self):
		return self.__width
	
	def setAllowBlank(self, allowBlank):
		self.__allowBlank = allowBlank
		
	def getAllowBlank(self):
		return self.__allowBlank
	
	fieldLabel = property(getFieldLabel, setFieldLabel)
	width = property(getWidth, setWidth)
	allowBlank = property(getAllowBlank, setAllowBlank)
	
class NumberField(Field):
	def __init__(self, page=None, name="numberfield", fieldLabel = "Textfield", width = 175, allowBlank = True):
		Field.__init__(self, page, name)
		self.__allowBlank = False
		self.__allowDecimals = True
		self.__allowNegative = True
		self.__decimalPrecision = 2
		self.__fieldLabel = fieldLabel
		self.__width = width
		self.fieldType = "float"
		self.value = 0.0
		
	def setAllowBlank(self, allowBlank):
		self.__allowBlank = allowBlank
	
	def getAllowBlank(self):
		return self.__allowBlank
	
	def setAllowDecimals(self, allowDecimals):
		self.__allowDecimals = allowDecimals
		if self.__allowDecimals:
			self.fieldType = "float"
		else:
			self.fieldType = "int"
		
	def getAllowDecimals(self):
		return self.__allowDecimals
	
	def setAllowNegative(self, allowNegative):
		self.__allowNegative = allowNegative

	def getAllowNegative(self):
		return self.__allowNegative

	def setDecimalPrecision(self, precision):
		self.__decimalPrecision = precision
		
	def getDecimalPrecision(self):
		return self.__decimalPrecision
	
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
		
	def setWidth(self, width):
		self.__width = width
		
	def getWidth(self):
		return self.__width
	
	def doSetupJavaScript(self):
		
		allowBlankString = "true"
		allowDecimalsString = "true"
		allowNegativeString = "true"

		if not self.__allowBlank:
			allowBlankString = "false"
		if not self.__allowDecimals:
			allowDecimalString = "false"
		if not self.__allowNegative:
			allowNegativeString = "false"
		
		self.addJS("var %s = new Ext.form.NumberField({applyTo: '%s', fieldLabel: '%s', name: '%s', width: %d, allowBlank: %s, allowNegative: %s, allowDecimal: %s, decimalPrecision: %d});" % (self.name, self.name, self.__fieldLabel, self.name, self.__width, allowBlankString, allowNegativeString, allowDecimalsString, self.decimalPrecision))
	
	def doRender(self):
		item = DIV(klass="x-form-item")
		label = LABEL(self.fieldLabel, label_for=self.name)
		item.append(label)
		element = DIV(klass="x-form-element")
		item.append(element)
		input = INPUT(type="text", name=self.name, id=self.name, value=str(self.value))
		item.append(input)
		return item	

	allowBlank = property(getAllowBlank, setAllowBlank)
	allowDecimal = property(getAllowDecimals, setAllowDecimals)
	allowNegative = property(getAllowNegative, setAllowNegative)
	decimalPrecision = property(getDecimalPrecision, setDecimalPrecision)
	fieldLabel = property(getFieldLabel, setFieldLabel)
	width = property(getWidth, setWidth)
	
class ButtonSet(Base):
	def __init__(self, page=None, name="buttonSet"):
		Base.__init__(self, page, name)
		self.__controls = []
		self.__align = "center"
		self.__padding = ["0.2em", "0.2em", "0.2em", "0.2em"]
		
	def clear(self):
		self.__controls = []
	
	def add(self, control):
		self.__controls.append(control)
		
	def setAlign(self, align):
		
		if align == "center":
			self.__align = align
		if align == "right":
			self.__align = align
		if align == "left":
			self.__align = align
			
	def getAlign(self):
		return self.__align
	
	def setPaddingLeft(self, value):
		self.__padding[0] = value
		
	def getPaddingLeft(self, value):
		return self.__padding[0]
	
	def setPaddingRight(self, value):
		self.__padding[1] = value
		
	def getPaddingRight(self):
		return self.__padding[1]
	
	def setPaddingTop(self, value):
		self.__padding[2] = value
		
	def getPaddingTop(self):
		return self.__padding[2]
	
	def setPaddingBottom(self, value):
		self.__padding[3] = value
		
	def getPaddingBottom(self):
		return self.__padding[3]
	
	def getControls(self):
		return self.__controls
		
	def doRender(self):
		buttonSet = DIV(align=self.__align, style="padding: %s %s %s %s;" % (self.__padding[0], self.__padding[2], self.__padding[2], self.__padding[3]))
	
		for control in self.__controls:
			buttonSet.append(control.renderToTag())
			
		return buttonSet
	
	align = property(getAlign, setAlign)
	paddingLeft = property(getPaddingLeft, setPaddingLeft)
	paddingRight = property(getPaddingRight, setPaddingRight)
	paddingTop = property(getPaddingTop, setPaddingTop)
	paddingBottom = property(getPaddingBottom, setPaddingBottom)
	controls = property(getControls, None)
		
class Button(Base):
	def __init__(self, page=None, name="button", text="Click me"):
		Base.__init__(self, page, name)
		self.__text = text
		self.__type = "submit"
		self.actionEnabled = True
		
	def doSetupJavaScript(self):
		pass
	
	def doRender(self):
		#input = INPUT(type="submit", name=self.actionName, id=self.actionName, value=self.__text, klass="x-btn")
		if self.actionEnabled:
			input = DIV(INPUT(type="submit", name=self.actionName, id=self.actionName, value=self.__text), style="display:inline;padding-right:1em;")
		else:
			input = DIV(INPUT(type="submit", name=self.name, id=self.name, value=self.__text), style="display:inline;padding-right:1em;")
		return input
	
	def setText(self, text):
		self.__text = text
		
	def getText(self):
		return self.__text
	
	def setType(self, type):
		self.__type = type
		
	def getType(self):
		return self.__type
	
	text = property(getText, setText)
	type = property(getType, setType)
	
class FieldSet(Base):
	def __init__(self, page=None, name="fieldset"):
		Base.__init__(self, page, name)
		self.__controls = []
		self.__legend = "Fieldset legend"
		
	def clear(self):
		self.__controls = []
	
	def add(self, control):
		self.__controls.append(control)
		
	def doSetupJavaScript(self):
		for control in self.__controls:
			self.addJS(control.renderJSToString())
			
	def doRender(self):
		fieldSet = FIELDSET()
		fieldSet.append(LEGEND(self.legend))
		
		for control in self.__controls:
			fieldSet.append(control.renderToTag())
			
		return fieldSet
							   
	def setLegend(self, legend):
		self.__legend = legend
		
	def getLegend(self):
		return self.__legend
	
	def recRetrieve(self, request):
		
		controlValues = {}
		
		for control in self.__controls:

			if isinstance(control, Field):
				control.retrieve(request)
				if not controlValues.has_key(control.name):
					controlValues[control.name] = control.value

			if isinstance(control, FieldSet):
				setValues = control.recRetrieve(request)
				
				for valueName in setValues.keys():
					if not controlValues.has_key(valueName):
						controlValues[valueName] = setValues[valueName]
				
		return controlValues
	
	def retrieve(self, request):
		self.__values = self.recRetrieve(request)
		
	def recUpdate(self, formDict):
		for control in self.__controls:
			if isinstance(control, Field):
				control.update(formDict)
			if isinstance(control, FieldSet):
				control.update(formDict)
		
	def update(self, formDict):
		self.recUpdate(formDict)
	
	legend = property(getLegend, setLegend)
	
class TextArea(Field):
	def __init__(self, page=None, name="textarea", fieldLabel = "textarea", rows=4, cols=80, width=200, readonly=False, allowBlank=False):
		Field.__init__(self, page, name)
		self.__rows = rows
		self.__cols = cols
		self.__width = width
		self.__readonly = False
		self.__fieldLabel = fieldLabel
		self.__allowBlank = allowBlank
		self.fieldType = "multistring"
		
	def doSetupJavaScript(self):
		flagString = "true"
		if not self.__allowBlank:
			flagString = "false"
		
		self.addJS("var %s = new Ext.form.TextArea({applyTo: '%s', name: '%s', width: %d, allowBlank: %s});" % (self.name, self.name, self.name, self.__width, flagString))
			
	def doRender(self):
		item = DIV(klass="x-form-item")
		label = LABEL(self.fieldLabel, label_for=self.name)
		item.append(label)
		element = DIV(klass="x-form-element")
		item.append(element)
		input = TEXTAREA(name=self.name, rows=str(self.__rows), cols=self.__cols, readonly=self.__readonly, id=self.name)
		for line in self.value:
			input.append(line+"\n")
		item.append(input)
		return item	
							   
	def setRows(self, rows):
		self.__rows = rows
		
	def getRows(self):
		return self.__rows
	
	def setCols(self, cols):
		self.__cols = cols
		
	def getCols(self):
		return self.__cols
	
	def setWidth(self, width):
		self.__width = width
		
	def getWidth(self):
		return self.__width
	
	def setReadonly(self, flag):
		self.__readonly = flag
		
	def getReadonly(self):
		return self.__readonly
	
	def setAllowBlank(self, flag):
		self.__allowBlank = flag
		
	def getAllowBlank(self):
		return self.__allowBlank
	
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel	
	
	rows = property(getRows, setRows)
	cols = property(getCols, setCols)
	width = property(getWidth, setWidth)
	readonly = property(getReadonly, setReadonly)
	allowBlank = property(getAllowBlank, setAllowBlank)
	fieldLabel = property(getFieldLabel, setFieldLabel)
	
class ComboBox(Field):
	def __init__(self, page=None, name="combobox", fieldLabel = "textarea"):
		Field.__init__(self, page, name)
		self.__fieldLabel = fieldLabel
		self.__typeAhead = True
		self.__triggerAction = 'all'
		self.__width = 120
		self.__forceSelection = True
		self.__options = []
		self.fieldType = "string"
		
	def add(self, caption, value):
		self.__options.append([caption, value])
		
	def clear(self):
		self.__options = []
		
	def doSetupJavaScript(self):
		typeAheadString = "true"
		forceSelectionString = "true"
		
		if not self.__typeAhead:
			typeAheadString = "false"
			
		if not self.__forceSelection:
			foceSelectionString = "false"
			
		self.addJS("var %s = new Ext.form.ComboBox({name: '%s', width: %d, typeAhead: %s, triggerAction: '%s', transform: '%s', forceSelection: %s});" % (self.name, self.name, self.__width, typeAheadString, self.triggerAction, self.name, forceSelectionString))
			
	def doRender(self):
		item = DIV(klass="x-form-item")
		label = LABEL(self.fieldLabel, label_for=self.name)
		item.append(label)
		element = DIV(klass="x-form-element")
		item.append(element)
		
		select = SELECT(name=self.name, id=self.name)
		for option in self.__options:
			select.append(OPTION(option[0], value=option[1]))
		
		item.append(select)
		return item	
							   
	def setWidth(self, width):
		self.__width = width
		
	def getWidth(self):
		return self.__width
	
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
	
	def setTypeAhead(self, flag):
		self.__typeAhead = flag
		
	def getTypeAhead(self):
		return self.__typeAhead
	
	def setTriggerAction(self, action):
		self.__triggerAction = self.__triggerAction
		
	def getTriggerAction(self):
		return self.__triggerAction
	
	def setForceSelection(self, flag):
		self.__forceSelection = flag
		
	def getForceSelection(self):
		return self.__forceSelection

	width = property(getWidth, setWidth)
	fieldLabel = property(getFieldLabel, setFieldLabel)
	typeAhead = property(getTypeAhead, setTypeAhead)
	triggerAction = property(getTriggerAction, setTriggerAction)
	forceSelection = property(getForceSelection, setForceSelection)
	
class CheckBox(Field):
	def __init__(self, page=None, name="checkbox", id="checkbox", fieldLabel = "Checkbox", value="value1"):
		Field.__init__(self, page, name)
		self.__fieldLabel = fieldLabel
		self.id = id
		self.fieldType = "checkbox"
		
	def doSetupJavaScript(self):
		self.addJS("var %s = new Ext.form.Checkbox({applyTo: '%s', fieldLabel: '%s', name: '%s', boxLabel:'%s'});" % (self.id, self.id, self.__fieldLabel, self.name, self.__fieldLabel))
	
	def doRender(self):
		item = DIV(klass="x-form-item")
		element = DIV(klass="x-form-element")
		item.append(element)
		if self.value:
			input = INPUT(type="checkbox", name=self.name, id=self.id, checked=self.value)
		else:
			input = INPUT(type="checkbox", name=self.name, id=self.id)			
		item.append(input)
		return item
	
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
	
	def retrieve(self, request):
		if self.getField(request, self.name) == None:
			self.value = False
		else:
			self.value = True

	fieldLabel = property(getFieldLabel, setFieldLabel)
		
class Radio(Field):
	def __init__(self, page=None, name="radio", id="radio", fieldLabel = "Radio", value="value1"):
		Field.__init__(self, page, name)
		self.__fieldLabel = fieldLabel
		self.__value = value
		self.id = id
		self.fieldType = "radio"
		self.value = False
		
	def doSetupJavaScript(self):
		self.addJS("var %s = new Ext.form.Radio({applyTo: '%s', fieldLabel: '%s', name: '%s', boxLabel:'%s'});" % (self.id, self.id, self.__fieldLabel, self.name, self.__fieldLabel))
	
	def doRender(self):
		item = DIV(klass="x-form-item")
		element = DIV(klass="x-form-element")
		item.append(element)
		
		if self.value:
			input = INPUT(type="radio", name=self.name, id=self.id, checked=self.value)
		else:
			input = INPUT(type="radio", name=self.name, id=self.id)
			
		item.append(input)
		return item
	
	def setFieldLabel(self, fieldLabel):
		self.__fieldLabel = fieldLabel
	
	def getFieldLabel(self):
		return self.__fieldLabel
	
	def setValue(self, value):
		self.__value = value
		
	def getValue(self):
		return self.__value
	
	def retrieve(self, request):
		if self.getField(request, self.name) == None:
			self.value = False
		else:
			self.value = True

	fieldLabel = property(getFieldLabel, setFieldLabel)
	value = property(getValue, setValue)
	
class Static(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name = "statictext")
		self.__text = ""
		self.__align = "center"
		
	def setText(self, text):
		self.__text = text
		
	def getText(self):
		return self.__text
	
	def setAlign(self, align):
		self.__align = align
		
	def getAlign(self):
		return self.__align
	
	def doRender(self):
		return P(self.__text, style="text-align:%s" % self.__align)
	
	text = property(getText, setText)
	align = property(getAlign, setAlign)
	
class Separator(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name = "separator")
	
	def doRender(self):
		return HR(klass="x-form-element")
	
class VSpace(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name = "space")
	
	def doRender(self):
		return BR(klass="x-form-element")
	
class MessageBox(Form):
	def __init__(self, page, name):
		Form.__init__(self, page, name)
		
		self.caption = "Information"
		self.actionEnabled = False
		
		self.__message = "Hello, world!"
		self.__returnPage = ""
		
		self.__messageStatic = Static(self, 'loginMessage')
		self.__messageStatic.text = self.__message

		self.add(VSpace(self, 's1'))
		self.add(self.__messageStatic)
		self.add(VSpace(self, 's1'))
		
		buttons = ButtonSet(self, 'buttons')
		self.__okButton = Button(self, 'messageOk', 'Ok')
		self.__okButton.actionEnabled = False
		self.__okButton.name = self.__returnPage
		buttons.add(self.__okButton)
		
		self.add(buttons)
		
	def setMessage(self, message):
		self.__message = message
		self.__messageStatic.text = self.__message
		
	def getMessage(self):
		return self.__message
	
	def setReturnPage(self, page):
		self.__returnPage = page
		self.name = self.__returnPage
		
	def getReturnPage(self):
		return self.__returnPage

	message = property(getMessage, setMessage)
	returnPage = property(getReturnPage, setReturnPage)
	
class Menu(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name)
		self.__items = []
		
	def clear(self):
		self.__items = []
		
	def add(self, caption, url, target="", features=""):
		self.__items.append({"caption":caption, "url":url, "target":target, "features":features})
		
	def getItems(self):
		return self.__items

	def doSetupJavaScript(self):
		#var informationMenu = new Ext.menu.Menu({id: 'informationMenu'})
		#informationMenu.add({text: 'Getting started...', handler: onGettingStartedClick})
		#informationMenu.add({text: 'Users guide...'})
		#informationMenu.add({text: 'Programming guide...'})
		
		self.addJS("var %s = new Ext.menu.Menu({id: '%s'});" % (self.id, self.id))
		
		for item in self.__items:
			if item["url"] != "":
				if item["target"]=="":
					self.addJS('%s.add({text:"%s", handler: function() {window.location="%s"}});' % (self.id, item["caption"], item["url"]))
				else:
					self.addJS('%s.add({text:"%s", handler: function() {window.open("%s", "", "%s")}});' % (self.id, item["caption"], item["url"], item["features"]))					
			else:
				self.addJS('%s.add({text:"%s"});' % (self.id, item["caption"]))
				
	
	def doRender(self):
		pass
	
	items = property(getItems, None)
	
class Toolbar(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name)
		
		self.__menus = []
		
	def clear(self):
		self.__menus = []
		
	def add(self, caption, menu):
		self.__menus.append({"caption":caption, "menu":menu})
		
	def getMenus(self):
		return self.__menus
		
	def doSetupJavaScript(self):
		#var mainMenuToolbar = new Ext.Toolbar('toolbar', {autoHeight:true});
		#mainMenuToolbar.add({text:'Information', menu: informationMenu });
		#mainMenuToolbar.add({text:'Session', menu: sessionMenu });
		#mainMenuToolbar.add({text:'Join', menu: joinMenu });
		#mainMenuToolbar.add({text:'Settings', menu: settingsMenu });
		#mainMenuToolbar.add({text:'Create', menu: createMenu });
		#mainMenuToolbar.add({text:'Manage', menu: manageMenu });
		#mainMenuToolbar.add({text:'Storage', menu: storageMenu });
		#mainMenuToolbar.add({text:'About', menu: aboutMenu });
		
		# Add menu javascript declarations
		
		for item in self.__menus:
			self.addJS(item["menu"].renderJSToString())
			
		# Create toolbar javascript declarations
		
		self.addJS("var %s = new Ext.Toolbar('%s');" % (self.id, self.id))
		
		for item in self.__menus:
			self.addJS('%s.add({text:"%s", menu: %s});' % (self.id, item["caption"], item["menu"].name))
		
	def doRender(self):
		return DIV(id=self.id)
	
	menus = property(getMenus, None)
	
		#var viewport = new Ext.Viewport({layout:'border', items:[
		#	{region:'north', contentEl: 'north', height: 52, title: 'Lunarc Application Portal', split:true },
		#	{region:'south', contentEl: 'south', split:true, height: 30, collapsible: true, margins:'0 0 0 0'},
		#	centerPanel = new Ext.Panel({region:'center', contentEl: 'center1', split:true, margins:'0 0 0 0'}),
		#	{region:'west', id:'west-panel', split:true, width: 200, minSize: 175, maxSize: 400, collapsible: true, margins:'0 0 0 5', layout:'accordion', layoutConfig:{ animate:true }, items: [
		#		jobTypePanel = new Ext.Panel({title:'Job types', border:false, iconCls:'nav'}),
		#		jobDefinitionPanel = new Ext.Panel({title:'Job definitions', border:false, iconCls:'nav'}),
		#		runningJobPanel = new Ext.Panel({title:'Running jobs', border:false, iconCls:'nav' }),
		#		storagePanel = new Ext.Panel({title:'Storage', border:false, iconCls:'nav'}),
		#	]}
		#]});

	
class Panel(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name)
		self.__config = {}
		self.__items = []
		
		self.__config["region"] = None
		self.__config["contentEl"] = None
		self.__config["height"] = None
		self.__config["width"] = None
		self.__config["title"] = None
		self.__config["split"] = True
		self.__config["collapsible"] = None
		self.__config["margins"] = None
		self.__config["minSize"] = None
		self.__config["maxSize"] = None
		self.__config["border"] = None
		self.__config["iconCls"] = None
		self.__config["layout"] = None
		self.__config["layoutConfig"] = None
		
		self.__animate = False
	
	def add(self, panel):
		self.__items.append(panel)
		
	def doSetupJavaScript(self):
		self.addJS("%s = new Ext.Panel(%s);" % (self.name, self.configString))
		if len(self.__items)>0:
			for extObj in self.__items:
				self.addJS(extObj.renderJSToString())
				self.addJS("%s.add(%s);" % (self.name, extObj.name))
				
	def doRender(self):
		contentEl = DIV(id=self.contentEl)
		
		for extObj in self.__items:
			contentEl.append(extObj.renderToTag())
			
		return contentEl

	def getConfigString(self):
		
		optionList = []
		
		if self.__config["layoutConfig"] == None:
			if self.__animate:
				self.__config["layoutConfig"] = "{ animate:true }"
			else:
				self.__config["layoutConfig"] = None
		
		for key in self.__config.keys():
			if self.__config[key]!=None:
				if key=='height' or key=='width' or key=='minSize' or key=='maxSize' or key=="split" or key=="collapsible" or key=="border" or key=="layoutConfig":
					optionList.append("%s: %s" % (key, str(self.__config[key]).lower()))
				else:
					optionList.append("%s: '%s'" % (key, str(self.__config[key])))
				
		configString = ', '.join(optionList)
		
		return "{ "+configString+" }"
	
	def setRegion(self, region):
		self.__config["region"] = region
		
	def getRegion(self):
		return self.__config["region"]
	
	def setContentEl(self, contentEl):
		self.__config["contentEl"] = contentEl
		
	def getContentEl(self):
		return self.__config["contentEl"]
	
	def setHeight(self, height):
		self.__config["height"] = height
		
	def getHeight(self):
		return self.__config["height"]
	
	def setWidth(self, width):
		self.__config["width"] = width
		
	def getWidth(self):
		return self.__config["width"]
	
	def setTitle(self, title):
		self.__config["title"] = title
		
	def getTitle(self):
		return self.__config["title"]

	def setSplit(self, split):
		self.__config["split"] = split
		
	def getSplit(self):
		return self.__config["split"]

	def setCollapsible(self, collapsible):
		self.__config["collapsible"] = collapsible
		
	def getCollapsible(self):
		return self.__config["collapsible"]

	def setMargins(self, margins):
		self.__config["margins"] = margins
		
	def getMargins(self):
		return self.__config["margins"]

	def setMinSize(self, minSize):
		self.__config["minSize"] = minSize
		
	def getMinSize(self):
		return self.__config["minSize"]

	def setMaxSize(self, maxSize):
		self.__config["maxSize"] = maxSize
		
	def getMaxSize(self):
		return self.__config["maxSize"]

	def setBorder(self, border):
		self.__config["border"] = border
		
	def getBorder(self):
		return self.__config["border"]

	def setIconCls(self, iconCls):
		self.__config["iconCls"] = iconCls
		
	def getIconCls(self):
		return self.__config["iconCls"]

	def setLayout(self, layout):
		self.__config["layout"] = layout
		
	def getLayout(self):
		return self.__config["layout"]

	def setLayoutConfig(self, layoutConfig):
		self.__config["layoutConfig"] = layoutConfig
		
	def getLayoutConfig(self):
		return self.__config["layoutConfig"]
	
	def setAnimate(self, flag):
		self.__animate = flag
		
	def getAnimate(self):
		return self.__animate
	
	region = property(getRegion, setRegion)
	contentEl = property(getContentEl, setContentEl)
	height = property(getHeight, setHeight)
	width = property(getWidth, setWidth)
	title = property(getTitle, setTitle)
	split = property(getSplit, setSplit)
	collapsible = property(getCollapsible, setCollapsible)
	margins = property(getMargins, setMargins)
	minSize = property(getMinSize, setMinSize)
	maxSize = property(getMaxSize, setMaxSize)
	border = property(getBorder, setBorder)
	iconCls = property(getIconCls, setIconCls)
	layout = property(getLayout, setLayout)
	layoutConfig = property(getLayoutConfig, setLayoutConfig)
	configString = property(getConfigString, None)
	animate = property(getAnimate, setAnimate)
	
class Viewport(Base):
	def __init__(self, page, name):
		Base.__init__(self, page, name)
		
		self.__panels = []
		self.__layout = "border"
		
	def add(self, panel):
		self.__panels.append(panel)
	
	def doSetupJavaScript(self):
		
		for extObj in self.__panels:
			self.addJS(extObj.renderJSToString())
		
		self.addJS("%s = new Ext.Viewport({layout: '%s', items: [" % (self.name, self.layout))
		i = 1
		if len(self.__panels)>0:
			for extObj in self.__panels:
				if i!=len(self.__panels):
					self.addJS("%s," % (extObj.name))
				else:
					self.addJS("%s" % (extObj.name))
		self.addJS("]});")
		
	def doRender(self):
		tag = DIV()

		for extObj in self.__panels:
			tag.append(extObj.renderToTag())
			
		return tag
		
	def getPanels(self):
		return self.__panels
	
	def setLayout(self, layout):
		self.__layout = layout
		
	def getLayout(self):
		return self.__layout
	
	panels = property(getPanels, None)
	layout = property(getLayout, setLayout)

if __name__ == "__main__":

	container = Container()
	form = Form(None, "testform")
	form.URL = "test"
	
	textField1 = TextField(None, 'textField1')
	textField1.fieldLabel = "Name"
	form.add(textField1)
	
	button = Button(None, 'button')
	form.add(button)
	
	container.add(form)
	print container.renderToString()
