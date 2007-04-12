###############################################
from MiscUtils.MixIn import MixIn
from WebKit.Session import Session

#from Lap.Log import *

import os, logging, time, stat

class SessionMixIn:
	
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
###############################################

