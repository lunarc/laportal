#
# ViewArcLogsPage
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

"""ViewArcLogsPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

from time import *
import os, sys, pwd, string, pickle, shutil, time

import Web
import Web.Ui

class ViewArcLogsPage(ApplicationSecurePage):
   
    def onInitPage(self):
        """
        Initialise JavaScript controls.
        """
        
        # Create dynamic table form 
        
        self._form = Web.Ui.TableForm("frmLogViewer", "", "ARC Logs", "100%", 5, 4)
        self._form.page = self
        self._form.sortColumn = 0
        self._form.sortType = "asc"
                
        self.addControl(self._form)
        
                
    def writeContent(self):
        """
        Render page HTML.
        """
        
        # Obtain log list from arcclient
        
        logList = self.arcClient.readLog()
        
        # Create form table with log entries
                
        self._form.clear()
        self._form.action = "ViewArcLogsPage"
        self._form.rows = len(logList)
        
        row = 0
        
        self._form.headers = ["Date", "Component", "Type", "Message"]
                                    
        for logEntry in logList:
            self._form.addNormalText(logEntry[0], row, 0)
            self._form.addNormalText(logEntry[1], row, 1)
            self._form.addNormalText(logEntry[2], row, 2)
            self._form.addNormalText(logEntry[3], row, 3)
            row = row + 1
            
        self._form.addFormButton("Clear log", "_action_clearLog") 
        
        self._form.haveSubmit = False
        self._form.haveButtons = True
        self._form.render(self)
        
    def clearLog(self):
        """
        Clear arcclient log.
        """
        self.arcClient.clearLog()
        self.writeBody()
    
    def actions(self):
        """
        Return a list of implemented actions.
        """
        return ApplicationSecurePage.actions(self) + ["clearLog"]
