from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes

from HyperText.HTML import *

import Web.Dialogs

class PleaseWaitPage(ApplicationSecurePage):
	def title(self):
		return 'Please Wait...'

	def writeHead(self):
		if self.request().hasField("URL"):
			slowURL = self.request().field("URL")
			self.writeln("""<META HTTP-EQUIV="REFRESH" CONTENT="0;URL=%s">""" % slowURL)

		ApplicationSecurePage.writeHead(self)

	def writeHTML(self):
		self.writeDocType()
		self.writeln('<html>')
		self.writeHead()
		self.writeBody()
		self.writeln('</html>')

	def writeContent(self):

		message = "Please, wait..."
		
		if self.request().hasField("Message"):
				message = self.request().field("Message")
		Web.Dialogs.pleaseWaitBox(self, message)
		self.response().flush()
