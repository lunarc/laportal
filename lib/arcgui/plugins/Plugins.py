#!/bin/env python

"""
Plugin support module
"""

import os, sys, arc

class PluginBase(object):
    """
    Base class for ArcGui plugins.
    """
    
    def __init__(self):
        self.__filename = "noname.lpi"
        self.onInit()
    
    def onInit(self):
        pass
 
    def onDestroy(self):
        pass
    
    def onEdit(self):
        pass
    
    def onSetup(self):
        pass
    
    def onClean(self):
        pass
    
    def onSave(self, workDir):
        pass
    
    def onLoad(self, workDir):
        pass
            
    def onGetId(self):
        return "PluginBase"
    
    def onGetVersion(self):
        return (0,0,0)
        
    def onGetShortName(self):
        return "Base plugin"
        
    def onGetDescription(self):
        return "Base plugin should not be used directly."
    
    def onNeedSave(self):
        return False
    
    def onGetTask(self):
        return None
    
    def getFilename(self):
        return self.__filename
    
    def setFilename(self, filename):
        self.__filename = filename
        
    def setWorkDir(self, workDir):
        self.__workDir = workDir
        
    def getWorkDir(self):
        return self.__workDir
    
    id = property(onGetId)
    version = property(onGetVersion)
    filename = property(getFilename, setFilename)
    shortname = property(onGetShortName)
    description = property(onGetDescription)
    workDir = property(getWorkDir, setWorkDir)
    task = property(onGetTask)
        
instance = None

class PluginManager(object): # subclassing from object for 2.2, unnecessary after that
    """
    Class for managing plugins in ArcGui.
    """
    def __new__(cls):
        """
        Overloaded new method to make sure we only have one instance
        of a plugin manager.
        """
        
        global instance
        
        if instance is not None:
            return instance
    
        instance = object.__new__(cls)
        return instance
    
    def logMsg(self, level, msg):
        if self.__logger!=None:
            self.__logger.msg(level, msg)
        
    def logInfoMsg(self, msg):
        if self.__logger!=None:
            self.logMsg(arc.INFO, msg)
    
    def logDebugMsg(self, msg):
        if self.__logger!=None:
            self.logMsg(arc.DEBUG, msg)

    def logErrorMsg(self, msg):
        if self.__logger!=None:
            self.logMsg(arc.ERROR, msg)    
    
    def __init__(self):
        """
        Plugin manager constructor.
        
        Loads plugins from plugin directory. Creates a dictionary of
        subclasses.
        """
        
        self.__logger = arc.Logger(arc.Logger_getRootLogger(), "PluginManager")
        
        self.logInfoMsg("Init plugin manager...")
        
        # Initialise instance variables
        
        self.__pluginPath = ""
        self.__pluginClassDict = {}
        
        # Figure out plugin directory
        
        if os.environ.has_key("ARCGUI_LIB"):
            self.__pluginPath = os.path.join(os.environ["ARCGUI_LIB"], "plugins")
        else:
            self.__pluginPath = "./plugins"

        self.logInfoMsg("Finding plugins...")
        
        # Find and load plugins
            
        dirList = os.listdir(self.__pluginPath)
        
        for dirItem in dirList:
            fullPath = os.path.join(self.__pluginPath, dirItem)
            if os.path.isfile(fullPath):
                if os.path.splitext(fullPath)[1] == ".py":
                    if dirItem!="Plugins.py":
                        self.__loadPlugin(dirItem.split(".py")[0])
        
        # Store loaded subclasses in a dictionary
                        
        for pluginClass in PluginBase.__subclasses__():
            self.__pluginClassDict[pluginClass.__name__] = pluginClass
            
                    
    def __loadPlugin(self, plugin):
        """
        Load plugin from plugin dir.
        """
        self.logInfoMsg("Importing: "+plugin)
        __import__(plugin)

    def getPlugins(self):
        return PluginBase.__subclasses__()
        
    def pluginFromId(self, pluginId):
        """
        Return plugin instance from string pluginId.
        """
        if self.__pluginClassDict.has_key(pluginId):
            return self.__pluginClassDict[pluginId]()
        else:
            return None
        
    def pluginFromWorkDir(self, workDir):
        """
        Return plugin instance based on definition dir.
        """
        pluginIdFilename = os.path.join(workDir, "plugin.id")
        if os.path.exists(pluginIdFilename):
            pluginIdFile = open(pluginIdFilename, "r")
            pluginId = pluginIdFile.read().strip()
            pluginIdFile.close()
            
            return self.pluginFromId(pluginId)
        else:
            return None
        
    plugins = property(getPlugins)
