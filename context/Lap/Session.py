#
# Session module
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

"""Session module"""

import string
import os
import sys
import pickle

import Grid.Security

from Lap.Log import *

import LapSite

class User:
	"""Class for handling the user setup structure
	
	The class will create the necessary directory structure for
	storing the user proxy, job directories etc. The directory
	structure is created from information in the DN. For example:
	
	/{Organisation}/{Org.unit}/{Username}
	"""
	def __init__(self, DNString):
		"""Class constructor.
		
		@type DNString: string
		@param DNString: String containing the X509 DN"""
		
		self._sessionDir = LapSite.Dirs["SessionDir"]

		DN = Grid.Security.DN(DNString)		
		self.setDN(DN)

		self._prefs = {}

		self._prefs["preferredCluster"] = ""
		self._prefs["defaultMail"] = ""
		self._prefs["submitTimeout"] = 4
		self._prefs["preferredClusters"] = []
		self._prefs["rejectedClusters"] = []
		
		self.createDir()

		# Load preferences if they exist

		self.loadPrefs()
		
	def updatePrefs(self):
		"""Update preferences with new properties."""
		if not self._prefs.has_key("preferredClusters"):
			self._prefs["preferredClusters"] = []
			if self._prefs["preferredCluster"]!="":
				self._prefs["preferredClusters"].append(self._prefs["preferredCluster"])
				self._prefs["preferredCluster"] = ""
				
		if not self._prefs.has_key("rejectedClusters"):
			self._prefs["rejectedClusters"] = []
				
	def setDN(self, DN):
		"""Set the DN instance managed by this class."""

		self._DN = DN
		
		# Make sure we don't have any spaces in the directory name
		
		self._userDirname = string.replace(self._DN.getName(), " ", "_")
		
		# Create the directory
		
		self._userDir = os.path.join(self._sessionDir,"%s/%s/%s" % (self._DN.getOrganisation2(), self._DN.getOrganisationalUnit(), self._userDirname))
		
	def getDN(self):
		"""Return the DN instance for this class."""
		return self._DN

	def checkAndMkdir(self, directory):
		"""Convenience function for checking and creating a directory."""
		if not os.path.exists(directory):
			os.mkdir(directory)

	def createDir(self):
		"""Create user directory."""
		if self._DN!=None:
			if not os.path.exists(self._userDir):
				self.checkAndMkdir(os.path.join(self._sessionDir,"%s" % self._DN.getOrganisation2()))
				self.checkAndMkdir(os.path.join(self._sessionDir,"%s/%s" % (self._DN.getOrganisation2(), self._DN.getOrganisationalUnit())))
				self.checkAndMkdir(os.path.join(self._sessionDir,"%s/%s/%s" % (self._DN.getOrganisation2(), self._DN.getOrganisationalUnit(), self._userDirname)))
				lapInfo("Creating user directory: "+self._userDir)
				self.savePrefs()

	def exists(self):
		"""Returns true if user directory already exists."""
		return os.path.isdir(os.path.join(self._sessionDir,"%s/%s/%s" % (self._DN.getOrganisation2(), self._DN.getOrganisationalUnit(), self._userDirname)))

	def getDir(self):
		"""Return user directory."""
		return self._userDir

	def getProxy(self):
		"""Return user proxy filename."""
		return self._userDir+"/lap_proxy"
		
	def setPreferredCluster(self, cluster):
		"""Set the user preferred cluster."""
		self.clearPreferredClusters()
		self.addPreferredCluster(cluster)
		self._prefs["preferredCluster"] = cluster
		
	def getPreferredCluster(self):
		"""Return preferred cluster."""
		return self._prefs["preferredCluster"]
	
	def addPreferredCluster(self, cluster):
		"""Add a preferred cluster to the list of preferred clusters."""
		self._prefs["preferredClusters"].append(cluster)
		
	def removePreferredCluster(self, cluster):
		"""Remove specified cluster from list of preferred clusters."""
		clusterList = self._prefs["preferredClusters"]
		
		for i in range(len(clusterList)):
			if clusterList[i] == cluster:
				del clusterList[i]
				break
			
	def clearPreferredClusters(self):
		"""Clear list of preferred clusters."""
		del self._prefs["preferredClusters"][0:len(self._prefs["preferredClusters"])]
		
	def assignPreferredClusters(self, clusterList):
		"""Assign a list of hostnames to the list of preferred clusters."""
		self.clearPreferredClusters()
		for cluster in clusterList:
			self.addPreferredCluster(cluster)
		
	def getPreferredClusters(self):
		"""Return list of preferred clusters."""
		return self._prefs["preferredClusters"]

	def addRejectedCluster(self, cluster):
		"""Add cluster to the list rejected clusters."""
		self._prefs["preferredClusters"].append(cluster)
		
	def removeRejectedCluster(self, cluster):
		"""Remove cluster from the list of rejected clusters."""
		clusterList = self._prefs["preferredClusters"]
		
		for i in range(len(clusterList)):
			if clusterList[i] == cluster:
				del clusterList[i]
				break
			
	def clearRejectedClusters(self):
		"""Clear list of rejected clusters."""
		del self._prefs["rejectedClusters"][0:len(self._prefs["rejectedClusters"])]
		
	def assignRejectedClusters(self, clusterList):
		"""Assign a list of hostnames to the list of rejected clusters."""
		self.clearRejectedClusters()
		for cluster in clusterList:
			self.addPreferredCluster(cluster)

	def getRejectedClusters(self):
		"""Return list of rejected clusters."""
		return self._prefs["rejectedClusters"]
		
	def setDefaultMail(self, mail):
		"""Set the user default mail."""
		self._prefs["defaultMail"] = mail
		
	def getDefaultMail(self):
		"""Return user default mail."""
		return self._prefs["defaultMail"]
		
	def setSubmitTimeout(self, timeout):
		"""Set the default submit timeout."""
		self._prefs["submitTimeout"] = timeout
		
	def getSubmitTimeout(self):
		"""Return the default submit timeout."""
		return self._prefs["submitTimeout"]
		
	def savePrefs(self):
		"""Save preferrences in the user.prefs file in the user directory."""
		userPrefFile = file(os.path.join(self._userDir, "user.prefs"), "w")
		pickle.dump(self._prefs, userPrefFile)
		userPrefFile.close()
	
	def loadPrefs(self):
		"""Load user preferrences from the user.prefs file in the user directory."""

		if os.path.exists(os.path.join(self._userDir, "user.prefs")):
			userPrefFile = file(os.path.join(self._userDir, "user.prefs"), "r")
			self._prefs = pickle.load(userPrefFile)
			self.updatePrefs()
			userPrefFile.close()
		else:
			self.savePrefs()
