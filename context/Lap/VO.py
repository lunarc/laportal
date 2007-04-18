#
# VO module
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

"""VO module"""

import string
import os
import sys

import Grid.ARC
import Lap.Utils

class VO(object):
	"""Abstract base class for implementing procedures for
	joining a VO."""
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
		"""Method for joining a VO should be implemented by this routine."""
		pass
	
	def remove(self):
		"""Method for removing user from VO should be implemented by this routine."""
		pass
	
	def setDescription(self, description):
		"""Set VO description."""
		self._description = description
		
	def getDescription(self):
		"""Return VO description."""
		return self._description
	
	def setURL(self, url):
		"""Set VO url."""
		self._url = url
		
	def getURL(self):
		"""Return VO URL."""
		return self._url
	
	def setName(self, name):
		"""Set VO Name."""
		self._name = name
		
	def getName(self):
		"""Return VO Name."""
		return self._name
	
	def	setRequesterEmail(self, mail):
		"""Set email address of requestor."""
		self._requesterEmail = mail
		
	def getRequesterEmail(self):
		"""Return email address of requestor."""
		return self._requesterEmail
	
	def setVOEmail(self, mail):
		"""Set VO mail address."""
		self._voEmail = mail
		
	def getVOEmail(self):
		"""Return VO email address."""
		return self._voEmail
	
	def setMailMessage(self, message):
		"""Set email message to send to VO administrator."""
		self._mailMessage = message
		
	def getMailMessage(self):
		"""Return email message to send VO administrator."""
		return self._mailMessage
	
	def setRequesterDN(self, DN):
		"""Set DN of requestor."""
		self._requesterDN = DN
		
	def getRequesterDN(self):
		"""Return DN of requestor."""
		return self._requesterDN
	
	def setExtraMessage(self, message):
		"""Set extra message."""
		self._extraMessage = message
		
	def getExtraMessage(self):
		"""Return extra message."""
		return self._extraMessage
	
	name = property(getName, setName)
	description = property(getDescription, setDescription)
	url = property(getURL, setURL)
	voEmail = property(getVOEmail, setVOEmail)
	requesterEmail = property(getRequesterEmail, setRequesterEmail)
	mailMessage = property(getMailMessage, setMailMessage)
	requesterDN = property(getRequesterDN, setRequesterDN)
	extraMessage = property(getExtraMessage, setExtraMessage)