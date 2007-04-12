import string
import os
import sys

import Grid.ARC
import Lap.Utils

class VO(object):
	def __init__(self):
		self._name = ""
		self._description = ""
		self._url = ""
		self._voEmail = ""
		self._requesterEmail = ""
		self._mailMessage = ""
		self._requesterDN = ""
		self._extraMessage = ""
	
	def join(self):
		pass
	
	def remove(self):
		pass
	
	def setDescription(self, description):
		self._description = description
		
	def getDescription(self):
		return self._description
	
	def setURL(self, url):
		self._url = url
		
	def getURL(self):
		return self._url
	
	def setName(self, name):
		self._name = name
		
	def getName(self):
		return self._name
	
	def	setRequesterEmail(self, mail):
		self._requesterEmail = mail
		
	def getRequesterEmail(self):
		return self._requesterEmail
	
	def setVOEmail(self, mail):
		self._voEmail = mail
		
	def getVOEmail(self):
		return self._voEmail
	
	def setMailMessage(self, message):
		self._mailMessage = message
		
	def getMailMessage(self):
		return self._mailMessage
	
	def setRequesterDN(self, DN):
		self._requesterDN = DN
		
	def getRequesterDN(self):
		return self._requesterDN
	
	def setExtraMessage(self, message):
		self._extraMessage = message
		
	def getExtraMessage(self):
		return self._extraMessage
	
	name = property(getName, setName)
	description = property(getDescription, setDescription)
	url = property(getURL, setURL)
	voEmail = property(getVOEmail, setVOEmail)
	requesterEmail = property(getRequesterEmail, setRequesterEmail)
	mailMessage = property(getMailMessage, setMailMessage)
	requesterDN = property(getRequesterDN, setRequesterDN)
	extraMessage = property(getExtraMessage, setExtraMessage)