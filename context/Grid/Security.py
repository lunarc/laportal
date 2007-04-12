#
# Grid security module
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

"""Grid security module."""

import os, sys, string

import Lap.System
import ARC

class DN:
	"""Distinguished Name class.
	
	This class maintains a X509 DN."""
	def __init__(self, DN):
		"""Class constructor
		
		Constructs the DN instance from a DN string.
		
		@type DN: string
		@param DN: String containing a X509 DN."""
		self.DNString = DN
		self.process()

	def process(self):
		"""Extract information from the DN string."""
		parts = string.split(self.DNString, "/")
		
		cleanedParts = []
			
		for part in parts:
			subPart = string.split(part,"=")
			if len(subPart)>1:
				cleanedParts.append(subPart[1])

		self.organisation1 = cleanedParts[0]
		self.organisation2 = cleanedParts[1]
		self.organisationalUnit = cleanedParts[2]
		self.name = cleanedParts[3]

	def getOrganisation1(self):
		"""Return string with the level 1 organisation."""
		return self.organisation1

	def getOrganisation2(self):
		"""Return string with the level 2 organisation."""
		return self.organisation2

	def getOrganisationalUnit(self):
		"""Return string with the organisational unit."""
		return self.organisationalUnit

	def getName(self):
		"""Return real name of user"""
		return self.name

	def setDNString(self, DNString):
		"""Assign a new DN string to the instance.

		@type DN: string
		@param DN: String containing a X509 DN."""
		
		self.DNString = DNString
		self.process()
		
	def getDNString(self):
		"""Return current DN string."""
		return self.DNString
	
	def getOriginalDN(self):
		"""Return DN without the /CN=Proxy part."""
		
		# Remove /CN=Proxy

		parts = string.split(self.DNString, "/")
		return string.join(parts[0:len(parts)-1], "/")

class Proxy:
	"""Proxy management class.
	
	This class handles a X509 proxy certificate."""
	def __init__(self, filename):
		"""Class constructor.
		
		@type  filename: string
		@param filename: Proxy filename"""
		self.proxyFilename = filename
		self.DN = ""
		self.timeleft = 0
		self._valid = False

		self.query()

	def setFilename(self, filename):
		"""Set the proxy filename."""
		self.proxyFilename = filename
		self.query()

	def getFilename(self):
		"""Return the proxy filename."""
		return self.proxyFilename
	
	def proxyInfoSubject(self):
		"""Return the proxy subject.
		
		@rtype: list
		@return: List consisting of [successFlag, subject, errorMessage]"""
		env = {}
		env["X509_USER_PROXY"] = self.proxyFilename
		resultVal, result = Lap.System.getstatusoutput("grid-proxy-info -subject", env)
		
		print resultVal
		
		if resultVal == 0:
			return True, result[0], ""
		else:
			errorMessage = "Unknown error"
			for line in result:
				if line.find("ERROR:")!=-1:
					if line.find("Couldn't read proxy")!=-1:
						errorMessage = "Could not read proxy."
			
			return False, "", errorMessage
	
	def proxyInfoTimeLeft(self):
		"""Return remaining proxy lifetime.
		
		@rtype: list
		@return: List consisting of [successFlag, timeLeft, errorMessage]"""
		env = {}
		env["X509_USER_PROXY"] = self.proxyFilename
		resultVal, result = Lap.System.getstatusoutput("grid-proxy-info -timeleft", env)
		
		if resultVal == 0:
			return True, int(result[0]), ""
		else:
			errorMessage = "Unknown error"
			for line in result:
				if line.find("ERROR:")!=-1:
					if line.find("Couldn't read proxy")!=-1:
						errorMessage = "Could not read proxy."
			
			return False, -1, errorMessage

	def query(self):
		"""Query for proxy subject and proxy lifetime."""
		self._valid = True
		
		subjectOk, self.DN, errorMessage = self.proxyInfoSubject()
		
		if not subjectOk:
			self._valid = False
			self.timeLeft = -1
			return
		
		timeLeftOk, self.timeLeft, errorMessage = self.proxyInfoTimeLeft()
		
		if not timeLeftOk:
			self._valid = False
			return
		
	def isValid(self):
		"""Return True if proxy is still valid."""
		return self._valid


	def getDN(self):
		"""Return X509 DN of proxy certificate (string)."""
		return self.DN

	def getTimeleft(self):
		"""Return the amount of time left on the proxy certificate (int)."""
		return self.timeLeft				
