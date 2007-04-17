#
# PleaseWaitPage
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

"""PleaseWaitPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes

from HyperText.HTML import *

import Web.Dialogs

class PleaseWaitPage(ApplicationSecurePage):
	"""Please wait page
	
	This page is used to display a please wait message for the user when
	waiting for slow page requests to complete. The page is called using the
	following request syntax:
	
	.../PleaseWaitPage?URL={URL of the slow page}
	
	The page automatically waits for the page until it is displayed, then
	redirects to this page (META HTTP-EQUIV="REFRESH"). """
	
	def title(self):
		"""Return page title."""
		return 'Please Wait...'

	def writeHead(self):
		"""Render page head."""
		if self.request().hasField("URL"):
			slowURL = self.request().field("URL")
			self.writeln("""<META HTTP-EQUIV="REFRESH" CONTENT="0;URL=%s">""" % slowURL)

		ApplicationSecurePage.writeHead(self)

	def writeHTML(self):
		"""Overidden writeHTML method from WebKit."""
		self.writeDocType()
		self.writeln('<html>')
		self.writeHead()
		self.writeBody()
		self.writeln('</html>')

	def writeContent(self):
		"""Render page HTML."""
		message = "Please, wait..."
		
		if self.request().hasField("Message"):
				message = self.request().field("Message")
		Web.Dialogs.pleaseWaitBox(self, message)
		self.response().flush()
