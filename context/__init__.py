#
# SessionMixIn
#
# Copyright (C) 2006-2008 Jonas Lindemann
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

"""SessionMixIn module"""

from MiscUtils.MixIn import MixIn
from WebKit.Session import Session

import os, logging, time, stat

import LapSite
import Lap.Log

class SessionMixIn:
	"""Special class for updating the Session class with routines for expiring
	sessions."""
	
	def removeUserProxy(self):
		"""Remove user proxy file before session is expired/invalidated."""
	
		if self.hasValue("user_proxy"):
			
			proxyFilename = self.value("user_proxy")
			DNString = self.value("authenticated_user")
			
			if proxyFilename!=None:
				if os.path.isfile(proxyFilename):
					os.chmod(proxyFilename, stat.S_IRWXU)
					os.remove(proxyFilename)
					#lapInfo("User %s logging out." % DNString)
					#lapDebug("Deleted user proxy.")
				else:
					pass
					#lapDebug("No user proxy found.")

		self.setValue("user_proxy", None)
		self.setValue("authenticated_user", None)
	
	def expiring(self):
		"""Let the session expire.

		Called when session is expired by the application.
		Subclasses should invoke super.
		Session store __delitem__()s should invoke if not isExpired().

		"""

		#lapDebug("Session, "+self.identifier()+" expiring.")
		
		# Remove user proxy file
		
		if self.isTimedOut():
			self.removeUserProxy()
		
		self._isExpired = 1
		
	def invalidate(self):
		"""Invalidate the session.

        It will be discarded the next time it is accessed.

        """

		#lapDebug("Session, "+self.identifier()+" invalidated.")

		self.removeUserProxy()
		
		self._lastAccessTime = 0
		self._values = {}
		self._timeout = 0
		
	def isTimedOut(self):
		"""Return True if the session has timedout, otherwise false"""
		return time.time() - self.lastAccessTime() > self.timeout()

# Now inject the methods from SessionMixIn into Session
MixIn(Session, SessionMixIn)

# Setup logging

Lap.Log.lapSetupLogging()
