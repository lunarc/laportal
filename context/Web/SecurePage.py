#
# SecurePage base class module
#
# Copyright (C) 2006-2009 Jonas Lindemann
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
from UserKit.RoleUserManagerToFile import RoleUserManagerToFile

# --- Must be replaced when used with Python 2.5 or higher
import sha

import Lap.Session
import Lap.Authorisation

from Lap.Log import *

import Grid.Security
import Grid.ARC

from Grid.Clients import ArcClient

import LapSite

class SecurePage(DefaultPage):
    """SecurePage base class
    
    The SecurePage base class serves as the base on which pages requiring
    authentication are built. The class contains routines for determining if
    the user has authenticated himself, if not the class redirects to a login page
    asking the user for credential. In case of the portal this means a valid
    proxy."""
    
    def awake(self, trans):
        DefaultPage.awake(self, trans) # awaken our superclass

        print "awake()"
        
        if True:

            # Handle four cases: login attempt, logout, already logged in, and not already logged in.

            session = trans.session()
            request = trans.request()
            app = trans.application()

            # Are they logging out?

            if request.hasField('logout'):

                # They are logging out. Clear all session variables:

                session.values().clear()
                request.setField('extra', 'You have been logged out.')
                request.setField('action', request.urlPath().split('/')[-1])
                app.forward(trans, 'LoginPage')

            # Are they already logged in?

            elif self.loggedInUser():
                return

            elif request.environ().has_key("REMOTE_USER"):
                # Are they logging in?
                print "has remoteUser"
                if not self.loginRemoteUser(request.remoteUser()):
                    request.setField('extra', 'Login failed. Please try again.')
                    request.setField('action', request.urlPath().split('/')[-1])
                    app.forward(trans, 'UserLoginPage')
                    
            # Is the session expired?

            elif request.isSessionExpired():

                # Login page with a "logged out" message.

                session.values().clear()
                request.setField('extra', 'Your session has expired.')
                request.setField('action', request.urlPath().split('/')[-1])
                app.forward(trans, 'LoginPage')


            elif request.hasField('login') \
                and request.hasField('username') \
                and request.hasField('password'):

                # They are logging in. Get login id and clear session:

                loginid = session.value('loginid', None)
                session.values().clear()

                # Get request fields:

                username = request.field('username')
                password = request.field('password')

                # Check if they can successfully log in.
                # The loginid must match what was previously sent.

                if request.field('loginid', 'nologin') == loginid \
                    and self.loginUser(username, password):

                    # Successful login.
                    # Clear out the login parameters:

                    request.delField('username')
                    request.delField('password')
                    request.delField('login')
                    request.delField('loginid')
                else:

                    # Failed login attempt; have them try again:

                    request.setField('extra', 'Login failed. Please try again.')
                    request.setField('action', request.urlPath().split('/')[-1])
                    app.forward(trans, 'LoginPage')
            else:

                # They need to log in.

                session.values().clear()

                # Send them to the login page:

                request.setField('action', request.urlPath().split('/')[-1])
                app.forward(trans, 'LoginPage')
        else:

            # No login is required.

            session = self.session()
            request = self.request()

            # Are they logging out?

            if request.hasField('logout'):

                # They are logging out.  Clear all session variables.

                session.values().clear()

            # Write the page:

            DefaultPage.writeHTML(self)

    def respond(self, trans):

        # If the user is already logged in, then process this request normally.
        # Otherwise, do nothing.
        # All of the login logic has already happened in awake().

        if self.loggedInUser():
            DefaultPage.respond(self, trans)

    def isValidUserAndPassword(self, username, password):
        """
        Validate user and password. Each user directory
        contains a user.passwd file containing the password
        hash for the user.
        """
        
        userDir = os.path.join(LapSite.Dirs["SessionDir"],username)
        userPasswdFilename = os.path.join(userDir,"user.passwd")
        
        if os.path.exists(userPasswdFilename):
            userPasswdFile = open(userPasswdFilename,"r")
            passwordHash = userPasswdFile.readline().strip()
            userPasswdFile.close()
            
            if passwordHash==sha.sha(password).hexdigest():
                return True
            
        return False
    
    def __dn2user(self, dn):
        parts = dn.split("/")[1:]
        
        dnParts = []
        
        for part in parts:
            id = part.split("=")[1]
            id = id.replace(".","_").lower()
            id = id.replace(" ","_")
            dnParts.append(id)
            
        return "_".join(dnParts)

    def loginRemoteUser(self, remoteUser):
        if remoteUser!="":
            self.session().setValue("authenticated_user", self.__dn2user(remoteUser))
            self.session().setValue("authenticated_user_dn", remoteUser)
            return True
        else:
            return False

    def loginUser(self, username, password):

        # We mark a user as logged-in by setting a session variable
        # called authenticated_user to the logged-in username.
        # Here, you could also pull in additional information about
        # this user (such as a user ID or user preferences) and store
        # that information in session variables.

        if self.isValidUserAndPassword(username, password):
            self.session().setValue('authenticated_user', username)
            return 1
        else:
            return 0

    def loggedInUser(self):

        # Gets the name of the logged-in user, or returns None
        # if there is no logged-in user.
        
        if self.session().hasValue("authenticated_user"):
            return self.session().value('authenticated_user')
        else:
            return None
        
    def loggedInUserDN(self):
        
        if self.session().hasValue("authenticated_user_dn"):
            return self.session().value('authenticated_user_dn')
        else:
            return None

    def defaultConfig(self):
        return {'RequireLogin': 1}

    def configFilename(self):
        return 'Configs/SecurePage.config'
    
    def oldInit(self):
        """Class constrcutor"""
        DefaultPage.__init__(self)
        
    # ----------------------------------------------------------------------
    # Get/set methods
    # ----------------------------------------------------------------------    
        
    def getLoggedInUser(self):
        """Gets the name of the logged-in user, or returns None if there is
        no logged-in user."""
        return self.session().value('authenticated_user', None)
    
    def getVOAdminUser(self):
        """Return name of configured administrative user."""
        return LapSite.Admin["VOAdmin"]

    def getUserAdminUser(self):
        """Return name of configured administrative user."""
        return LapSite.Admin["UserAdmin"]

    # ----------------------------------------------------------------------
    # Methods
    # ----------------------------------------------------------------------    

    def isVOAdminUser(self):
        """Return true if current user is administrative user."""
        return self.getLoggedInUser() == self.getVOAdminUser()
    
    def isUserAdminUser(self):
        """Return true if current user is administrative user."""
        return self.getLoggedInUser() == self.getUserAdminUser()

    # ----------------------------------------------------------------------
    # Overidden methods (WebKit)
    # ----------------------------------------------------------------------            

    def awake2(self, trans):
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
                    pass
            
            # Check if they can successfully log in.  The loginid must match what was previously
            # sent.
            
            if request.field('loginid', 'nologin')==loginid and self.loginUser(proxy):
                # Successful login.
                # Clear out the login parameters
                request.delField('proxy')
            else:
                # Failed login attempt; have them try again.
                request.setField('extra', 'Login failed.  Please try again.')
                
                url = "/LoginPage" 
                app.forward(trans, url)

        # They aren't logging in; are they already logged in?
        
        elif not self.getLoggedInUser():

            # They need to log in.
            
            url = "/LoginPage"
            app.forward(trans, url)


    def respond2(self, trans):
        """If the user is already logged in, then process this request normally.  Otherwise, do nothing.
        All of the login logic has already happened in awake().
        """
        if self.getLoggedInUser():
            DefaultPage.respond(self, trans)


    def loginUser2(self, proxyContent):
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
            
            # If user authenticated, check authorisation
            
            if Lap.Authorisation.isUserAuthorised(DNString):
                self.session().setValue('authenticated_user', DNString)
                self.session().setValue('user_proxy', user.getProxy())
                lapInfo("User %s logged in." % DNString)
                return 1
            else:
                lapInfo("User %s not authorised." % DNString)
                self.session().setValue('authenticated_user', None)
                self.session().setValue('user_proxy', None)
                return 0


        else:
            lapInfo("User % failed login, proxy expired.")
            self.session().setValue('authenticated_user', None)
            self.session().setValue('user_proxy', None)
            return 0
        
    def getArcClient(self):
        if self.session().hasValue("authenticated_user"):
            if self.session().hasValue("tmp_arcClient"):
                return self.session().value("tmp_arcClient")
            else:
                # Create arcclient instance
                user = Lap.Session.User(self.session().value('authenticated_user'))
                
                userDir = user.getDir();
                proxyFilename = os.path.join(userDir, "proxy.pem")
                jobListFilename = os.path.join(userDir, "jobs.xml")
                userConfigurationFilename = os.path.join(userDir, "client.xml")
                logFilename = os.path.join(userDir, "client.log")
                arcClient = ArcClient(proxyFilename, jobListFilename, userConfigurationFilename, logFilename)
                arcClient.loadJobList()
                
                # Store the arcclient instance as a temporary session variable.
                # A special session store is used to exclude the instance
                # variable to be pickled to disk.
                
                self.session().setValue("tmp_arcClient", arcClient)
                return arcClient
        else:
            return None
        
    arcClient = property(getArcClient)


    # ----------------------------------------------------------------------
    # Obsolete methods
    # ----------------------------------------------------------------------            

    def defaultConfig2(self):
        return {'RequireLogin': 1}

    def configFilename2(self):
        return 'Configs/SecurePage.config'
