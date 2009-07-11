#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
# generated by wxGlade HG on Sun May 31 17:14:53 2009

#
# ArcGui main application class
#
# Copyright (C) 2008-2009 Jonas Lindemann
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

import os, sys
   
# Import and check for ARC1 Python binding
    
try:
    import arc
except:
    print "ARC1 Python binding not found. Please check search paths."
    sys.exit(-1)
    
# Import and check for wxPython binding
    
try:
    import wx
except:
    print "wxPython is not found. Please check search paths."
    sys.exit(-1)
    
# Import and check for arcgui classes
    
try:
    from ArcWindow import ArcWindow
except:
    print "Classes needed for arcgui operation not found. Please check setup."
    sys.exit(-1)
    
        
    
# Define arcgui application class ArcClientApp

class ArcClientApp(wx.App):
    def OnInit(self):
        wx.InitAllImageHandlers()
        mainWindow = ArcWindow(None, -1, "")
        self.SetTopWindow(mainWindow)
        mainWindow.Show()
        return 1

# end of class ArcClientApp

# Initiate and start arcgui application

if __name__ == "__main__":
    
    arcgui = ArcClientApp(0)
    arcgui.MainLoop()
