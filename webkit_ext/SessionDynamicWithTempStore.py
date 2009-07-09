import time, threading

from WebKit.SessionStore import SessionStore
from WebKit.SessionDynamicStore import SessionDynamicStore
import WebKit.SessionMemoryStore, WebKit.SessionFileStore

debug = 0


class SessionDynamicWithTempStore(SessionDynamicStore):
    """
    Session store with support for temporary session variables.
    Temporary session variables are not stores when the server is
    shutdown. This can be used to store pointers to swig libraries
    which are difficult to serialise.
    """
    def __init__(self, app):
        # Create both a file store and a memory store
        print "Init SessionDynamicWithTempStore()"
        SessionDynamicStore.__init__(self, app)

    def isTempSession(self, key):
        """
        All sessions names with prefix tmp_ are considered
        temporary and not stored on server shutdown.
        """
        print "isTempSession(%s) = %s" % (key, key.find("tmp_")!=-1)
        return key.find("tmp_")!=-1
        
    def removeSessionTemp(self, session):
        """
        Remove temporary session variables from session
        """       
        sessionVars = session.values().keys()
        
        removedVars = {}
        
        for sessionVar in sessionVars:
            print sessionVar
            if sessionVar.find("tmp_")!=-1:
                print "Removing", sessionVar, "from session."
                removedVars[sessionVar] = session.value(sessionVar)
                session.delValue(sessionVar)
            
        return removedVars
    
    def addSessionTemp(self, session, tempSessionVars):
        """
        Add removed session variables to session
        """
        for sessionVar in tempSessionVars.keys():
            session.setValue(sessionVar, tempSessionVars[sessionVar])
            
    def moveToFile(self, key):
        tempSessionVars = self.removeSessionTemp(self._memoryStore[key])
        SessionDynamicStore.moveToFile(self,key)

    #def storeAllSessions(self):
    #    """
    #    Overridden storeAllSession to enable the use of
    #    temporary session variables (not stored at shutdown).
    #    """
    #    print "storeAllSessions()"
    #    self._lock.acquire()
    #    try:
    #        for i in self._memoryStore.keys():
    #            # Remove temporary session variables from session
    #            tempSessionVars = self.removeSessionTemp(self._memoryStore[i])
    #            self.moveToFile(i)
    #    finally:
    #        self._lock.release()

