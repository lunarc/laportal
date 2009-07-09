import string
import os
import sys
import smtplib

from Lap.VO import VO
import Lap.Utils

class CustomVO(VO):
	def __init__(self):
		self.name = "SweGrid VO"
		self.description = """SweGrid VO enables the use of the SweGrid resources
from the grid portal and from the ARC command line tools. To be accepted as a SweGrid
user the user must have an existing SNIC project."""
		self.url = "http://www.swegrid.se"
		self.voEmail = "lunarc-account-request@lunarc.lu.se"
		self.requesterEmail = ""
		self.mailMessage = """This is a request to join the SweGrid VO. The DN for the requesting user is:

%s

This message is generated on behalf of the user by the Lunarc Application Portal."""
		
	def join(self):
		
		errorMessage = ""
		
		mailSent = True
		
		message = """Subject: [ SweGrid VO join request ]\n"""
		message = message + self.mailMessage
		
		print "join():  self.requesterEmail = ", self.requesterEmail
		
		if self.requesterEmail!="":
		
			try:
				server = smtplib.SMTP("localhost")
				server.sendmail(self.requesterEmail, self.voEmail, message % self.requesterDN)
				server.quit()
			except smtplib.SMTPServerDisconnected:
				errorMessage = "The server unexpectedly disconnected."
				mailSent = False
			except smtplib.SMTPSenderRefused:
				errorMessage = "Sender refused."
				mailSent = False
			except smtplib.SMTPRecipientsRefused:
				errorMessage = "Recipient refused."
				mailSent = False
			except smtplib.SMTPDataError:
				errorMessage = "Mail server refused to accept the data."
				mailSent = False
			except smtplib.SMTPConnectError:
				errorMessage = "Could not connect to mail server."
				mailSent = False
			except smtplib.SMTPHeloError:
				errorMessage = "Mail server did not say hello..."
				mailSent = False
				
		else:
			errorMessage = "Sender not specified."
			mailSent = False
			
		if not mailSent:
			return errorMessage
		else:
			return None
	
	def remove(self):
		pass