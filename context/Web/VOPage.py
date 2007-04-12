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
import Web.Dialogs

class VOPage(ApplicationSecurePage):
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

	def writeContent(self):
		
		adapterName = self.request().adapterName()
		
		pageAddress = self.onGetPageAddress()

		vo = self.onCreateVO()
		
		if vo == None:
			Web.Dialogs.messageBox("No VO returned.", "Message")
			return

		if self.session().hasValue("vopage_status"):
		
			# -----------------------------------
			# Show any form messages
			# -----------------------------------
			
			if self.session().value("vopage_status")<>"":
				Web.Dialogs.messageBox(self, self.session().value("vopage_status"), "Message", self.session().value("vopage_return_page"))

			self.session().delValue("vopage_status")
			self.session().delValue("vopage_return_page")
		else:
			
			# -----------------------------------
			# Create VO form
			# -----------------------------------
			
			form = Web.Ui.Form("testform", pageAddress, "Join %s" % (vo.name) , width="30em")
			form.beginFieldSet("VO Information")
			form.addNormalText(vo.description)
			form.endFieldSet()
			form.beginFieldSet("User Information")
			form.addNormalText("You will be joined to the VO as:<br><br>")
			form.addNormalText(self.session().value('authenticated_user'))
			form.endFieldSet()
			form.beginFieldSet("Additional information")
			form.addTextArea("Messsage to VO", "voMessage", cols=40)
			form.endFieldSet()
			form.setHaveSubmit(False)
			form.addFormButton("Join", "_action_join")
			form.addFormButton("Back", "_action_back")
			form.render(self)
			
			# -----------------------------------
			# Show any form info messages
			# -----------------------------------
			
			if self.session().hasValue("vopage_info"):
				if self.session().value("vopage_info")<>"":
					Web.Dialogs.infoBox(self, self.session().value("vopage_info"), "Information", form.getWidth())
				self.session().delValue("vopage_info")
			
			
	def sleep(self, transaction):
		
		print "sleep:"
			
		ApplicationSecurePage.sleep(self, transaction)

	def actions(self):
		return ApplicationSecurePage.actions(self) + ["join", "back"]

	# ----------------------------------------------------------------------
	# Form action methods
	# ----------------------------------------------------------------------			

	def join(self):
		
		voMessage = self.request().field("voMessage")

		vo = self.onCreateVO()
		user = Lap.Session.User(self.session().value('authenticated_user'))
		vo.requesterEmail = user.getDefaultMail()
		vo.requesterDN = self.session().value('authenticated_user')
		vo.extraMessage = voMessage
		result = vo.join()
		
		if result!=None:
			self.setFormStatus(result)
		else:
			self.setFormStatus("VO joining request has been sent.", self.onFinishPageName())
			
		self.writeBody()
		
	def back(self):
		adapterName = self.request().adapterName()
		self.sendRedirectAndEnd("%s/context/SecureWelcomePage" % adapterName)

	# ----------------------------------------------------------------------
	# VOPage Event methods (Callbacks)
	# ----------------------------------------------------------------------			
		
	def onFinishPageName(self):
		"""Return name of return page after a VO request has finished. (Optional)""" 
		return "SecureWelcomePage"

	def onReturnPageName(self):
		"""Return name of page to return to for a message box. (Optional)"""
		return "SecureWelcomePage"
	
	def onCreateVO(self):
		"""Return an instance of a VO class used for the derived VOPage class. (Must implement)."""
		return None
	
	def onGetPageAddress(self):
		"""Return the page address of the derived VOPage class. (Must implement)."""
		return "VOPage"
