#
# SecurePage base class module
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

"""JobPage base class module"""

import string, types, os, stat
from DefaultPage import DefaultPage
from MiscUtils.Funcs import uniqueId

import Lap.Session
from Lap.Log import *

import Grid.Security
import Grid.ARC

import LapSite

from arclib import *

class SecurePage(DefaultPage):
	"""SecurePage base class
	
	The SecurePage base class serves as the base on which pages requiring
	authentication are built. The class contains routines for determining if
	the user has authenticated himself, if not the class redirects to a login page
	asking the user for credential. In case of the portal this means a valid
	proxy."""
	def __init__(self):
		"""Class constrcutor"""
		DefaultPage.__init__(self)
		
	# ----------------------------------------------------------------------
	# Get/set methods
	# ----------------------------------------------------------------------	
		
	def getLoggedInUser(self):
		"""Gets the name of the logged-in user, or returns None if there is
		no logged-in user."""
		return self.session().value('authenticated_user', None)
	
	def getAdminUser(self):
		"""Return name of configured administrative user."""
		return LapSite.Admin["VOAdmin"]

	# ----------------------------------------------------------------------
	# Methods
	# ----------------------------------------------------------------------	

	def isVOAdminUser(self):
		"""Return true if current user is administrative user."""
		return self.getLoggedInUser() == self.getAdminUser()
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			

	def awake(self, trans):
		"""Servlet awake method (overidden)
		
		Check for different page states, such as logout, login, already logged in
		and not already logged in."""
		
		# Awaken our superclass
		
		DefaultPage.awake(self, trans)

		# Handle four cases: logout, login attempt, already logged in, and not already logged in.
		
		session = trans.session()
		request = trans.request()
		
		app = trans.application()
		
		# Get login id and immediately clear it from the session
		
		loginid = session.value('loginid', None)
		if loginid:
			session.delValue('loginid')
		
		# Are they logging out?
		
		if request.hasField('logout'):
			
			lapInfo("User %s logged out." % self.session().value("authenticated_user"))

			# They are logging out.  Clear all session variables and take them to the
			# Login page with a "logged out" message.
			
			session.invalidate()
			request.setField('extra', 'You have been logged out.')
			request.setField('action', string.split(request.urlPath(), '/')[-1])
			
			adapterName = self.request().adapterName()
			url = "LoginPage" 
			app.forward(trans, url)
		
		elif request.hasField('login') and request.hasField('proxy'):
			
			lapInfo("User logging in.")
			print "User logging in."
			
			# They are logging in.  Clear session
			
			session.values().clear()
			
			# Get request fields
			
			proxy = None
			
			if request.hasField("proxy"):
				
				lapInfo("Downloading proxy.")

				ok = True
				try:
					f = request.field("proxy")
					proxy = f.file.read()
				except:
					lapWarning("Could not read proxy.")
					proxy = None
			
			# Check if they can successfully log in.  The loginid must match what was previously
			# sent.
			
			if request.field('loginid', 'nologin')==loginid and self.loginUser(proxy):
				# Successful login.
				# Clear out the login parameters
				request.delField('proxy')
			else:
				# Failed login attempt; have them try again.
				session.invalidate()
				request.setField('extra', 'Login failed.  Please try again.')
				url = "/LoginPage"
				app.forward(trans, url)

		# They aren't logging in; are they already logged in?
		
		elif not self.getLoggedInUser():

			# They need to log in.
			
			url = "/LoginPage"
			app.forward(trans, url)


	def respond(self, trans):
		"""If the user is already logged in, then process this request normally.  Otherwise, do nothing.
		All of the login logic has already happened in awake().
		"""
		if self.getLoggedInUser():
			DefaultPage.respond(self, trans)


	def loginUser(self, proxyContent):
		"""Log in user
		
		This routine logs in a user using a grid proxy certificate uploaded
		by the user."""
		
		# Does the proxy contain anything ??
		
		if proxyContent == None:
			return 0

		# Check if proxy is valid

		UID = uniqueId()

		filename = "/tmp/lap_%s" % (UID)

		tempFile = file(filename, "w")

		for line in proxyContent:
				tempFile.write(line)

		tempFile.close();

		os.chmod(filename, stat.S_IRUSR)
		
		proxyOk = True
		proxyExpired = True
		DNString = ""
		
		try:
			proxyCert = Certificate(PROXY, filename)
			DNString = proxyCert.GetIdentitySN()
			proxyExpired = proxyCert.IsExpired()
		except CertificateError, message:
			lapError(message)
			proxyOk = False

		#proxy = Grid.Security.Proxy(filename)
		#DNString = proxy.getDN()
		#timeLeft = proxy.getTimeleft()

		os.chmod(filename, stat.S_IRWXU)
		os.remove(filename)

		# Check to make sure that the proxy has not expired

		#if timeLeft>0 and proxy.isValid():
		if (not proxyExpired) and proxyOk:

			# Create a user (and directory)
			
			user = Lap.Session.User(DNString)
			
			# There should not be an existing proxy, but
			# delete it anyway.
			
			if os.path.exists(user.getProxy()):
				os.chmod(user.getProxy(), stat.S_IRWXU)
				os.remove(user.getProxy())

			proxyFile = file(user.getProxy(), "w")

			for line in proxyContent:
				proxyFile.write(line)

			proxyFile.close()
			proxyContent = []

			# Make sure it is not world-readable			

			#os.chown(user.getProxy(), 0, 0)
			os.chmod(user.getProxy(), stat.S_IRUSR)

			# Ok, user is authenticated

			self.session().setValue('authenticated_user', DNString)
			self.session().setValue('user_proxy', user.getProxy())
			
			lapInfo("User %s logged in." % DNString)

			return 1

		else:
			lapInfo("User % failed login, proxy expired.")
			self.session().setValue('authenticated_user', None)
			self.session().setValue('user_proxy', None)
			return 0

	# ----------------------------------------------------------------------
	# Obsolete methods
	# ----------------------------------------------------------------------			

	def defaultConfig(self):
		return {'RequireLogin': 1}

	def configFilename(self):
		return 'Configs/SecurePage.config'
