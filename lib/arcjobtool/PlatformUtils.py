
import sys, subprocess, os, wx, platform

def editFile(filename, wait=True):
    
    editor = ""
    
    if platform.system() == "Linux":
        editor = "gedit %s"
    
    if platform.system() == "Windows":
        editor = "wordpad %s"
        
    if platform.system() == "Darwin":
        editor = "open -a TextEdit %s"
        
    retcode = -1

    if editor != "":
        if os.path.isfile(filename):
            if wait:
                retcode = wx.Execute(editor % filename, wx.EXEC_SYNC)
            else:
                retcode = wx.Execute(editor % filename, wx.EXEC_ASYNC)
                
    return retcode

def showDir(directory, wait=False):

    fileBrowser = ""
    
    if platform.system() == "Linux":
        fileBrowser = "nautilus %s"
    
    if platform.system() == "Windows":
        fileBrowser = "explorer %s"
        
    if platform.system() == "Darwin":
        fileBrowser = "open %s"
        
    retcode = -1

    if fileBrowser != "":
        if os.path.isdir(directory):
            if wait:
                retcode = wx.Execute(fileBrowser % directory, wx.EXEC_SYNC)
            else:
                retcode = wx.Execute(fileBrowser % directory, wx.EXEC_ASYNC)
                
    return retcode


