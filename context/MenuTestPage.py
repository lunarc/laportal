#
# VOPage base class module
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

"""VOPage class module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from time import *

import os
import sys
import pwd
import string
import pickle

import Grid.ARC

import Lap
import Lap.Session

import Web
import Web.Ui
import Web.UiControls
import Web.Dialogs

class MenuTestPage(ApplicationSecurePage):
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
		
	def setFormInfo(self, status):
		self.session().setValue("vopage_info", status)		

	def setFormStatus(self, status, returnPage = ""):
		
		print "setFormStatus:"
		
		adapterName = self.request().adapterName()

		if returnPage=="":
			returnPage = self.onReturnPageName()

		print "returnPage = ", returnPage
		
		self.session().setValue("vopage_status", status)
		self.session().setValue("vopage_return_page", returnPage)	
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			

	def awake(self, transaction):
		print "awake:"
		ApplicationSecurePage.awake(self, transaction)
		
	def onInit(self, adapterName):
		
		self._form = Web.Ui.ExtForm(self, "testform", "MenuTestPage", "Join" , width="400px")
		self._form.beginFieldSet("VO Information")
		self._form.addControl(Web.UiControls.TextControl(name="test_new1", caption="NewControl", value="test1", size="10"))
		self._form.addControl(Web.UiControls.TextControl(name="test_new2", caption="NewControl", value="test2", size="20"))
		self._form.addControl(Web.UiControls.TextControl(name="test_new3", caption="NewControl", value="test3", size="30"))
		self._form.endFieldSet()
		self._form.beginFieldSet("User Information")
		self._form.addNormalText("You will be joined to the VO as:<br><br>")
		self._form.addNormalText(self.session().value('authenticated_user'))
		self._form.endFieldSet()
		self._form.beginFieldSet("Additional information")
		self._form.addControl(Web.UiControls.TextAreaControl(name="test_new4", caption="Message To VO", value="test1"))
		self._form.addControl(Web.UiControls.ButtonControl(name="test_new5", caption="Message To VO"))
		self._form.endFieldSet()
		self._form.setHaveSubmit(False)
		self._form.addFormButton("Hide", "_action_hide")
		
		self.addExtControl(self._form)

		self._messageBox = Web.Ui.ExtForm(self, "messageForm", "MenuTestPage", "Show", width="300px")
		self._messageBox.addNormalText("Show form again...")
		self._messageBox.addFormButton("Show", "_action_show")
		self._messageBox.hide()
		
		self.addExtControl(self._messageBox)

	#def writeContent(self):
	#	
	#	adapterName = self.request().adapterName()
	#	
	#	if self.session().hasValue("vopage_status"):
	#	
	#		# -----------------------------------
	#		# Show any form messages
	#		# -----------------------------------
	#		
	#		if self.session().value("vopage_status")<>"":
	#			Web.Dialogs.messageBox(self, self.session().value("vopage_status"), "Message", self.session().value("vopage_return_page"))
	#
	#		self.session().delValue("vopage_status")
	#		self.session().delValue("vopage_return_page")
	#	else:
	#		
	#		# -----------------------------------
	#		# Create VO form
	#		# -----------------------------------
	#		
	#		
	#		# -----------------------------------
	#		# Show any form info messages
	#		# -----------------------------------
	#		
	#		if self.session().hasValue("vopage_info"):
	#			if self.session().value("vopage_info")<>"":
	#				Web.Dialogs.infoBox(self, self.session().value("vopage_info"), "Information", form.getWidth())
	#			self.session().delValue("vopage_info")
			
	def actions(self):
		return ApplicationSecurePage.actions(self) + ["show", "hide"]
	
	def onUseExtJS(self):
		return True

	# ----------------------------------------------------------------------
	# Form action methods
	# ----------------------------------------------------------------------			

	def show(self):
		self._form.show()
		self._messageBox.hide()
		self.redrawForm()
		
	def hide(self):
		self._form.hide()
		self._messageBox.show()
		self.redrawForm()