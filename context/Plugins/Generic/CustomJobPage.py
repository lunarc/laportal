#
# LAP Generic Plugin - Version 0.9
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

from Web.JobPage import JobBasePage
from time import *
import os, sys, pwd, string, pickle

import Web
import Plugins.Generic.CustomJob

pluginName = "Generic"

class CustomJobPage(JobBasePage):
    
    def actions(self):
        """
        Return available actions.
        """
        return JobBasePage.actions(self) + ["clearInputFiles", "removeInputFiles"]
        
    def onGetFileTransferFields(self):
        """
        Return file transfer fields for the page.
        """
        return ["inputFile"]

    def onInitPage(self):
        """
        Initialise JavaScript controls.
        """
        tabControl = Web.Ui.jQueryTabs(self)
        tabControl.name = "tabs"
        self.addControl(tabControl)
    
    def onGetPageAddress(self):
        """
        Return page address of plugin.
        """
        return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
    
    def onCreateNewTask(self):
        """
        Create the derived task class and return it to the parent class.
        """
    
        task = Plugins.Generic.CustomJob.CustomTask()
        task.taskEditPage = "/Plugins/%s/CustomJobPage" % pluginName
        return task

    def onCreateEditJobForm(self, task):
        """
        Create the form used when editing an existing job definition
        is created.
        """
    
        form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit Generic job", width="32em")
              
        form.beginFieldSet("Job description")
        form.addTextArea("", "jobDescriptionString", task.jobDescriptionString, rows=10, cols=40, fieldType="raw")
        form.endFieldSet()
                
        form.beginFieldSet("Input files")
        form.beginSelect("Input files", "inputFiles", size=4, width="20em")
        for inputFile in task.inputFiles:
            form.addOption(inputFile)
        form.endSelect()
        form.addBreak()
        form.addFile("Add file(s)", "inputFile", "")
        form.addBreak()
        form.addBreak()
        form.beginIndent("9.0em")
        form.addSubmitButton("Upload", "_action_uploadFile")
        form.addSubmitButton("Clear", "_action_clearInputFiles")
        form.addSubmitButton("Remove", "_action_removeInputFiles")
        form.endIndent()
        form.endFieldSet()

        form.beginFieldSet("Job")
        form.addText("CPU time (min)", "cpuTime", task.cpuTime, fieldType="int")
        form.addBreak()
        form.addText("Job name", "jobName", task.name)
        form.addBreak()
        form.addText("Email notification", "email", task.notify, fieldType="email")
        form.addHidden("", "oldJobName", task.name)
        form.endFieldSet()
                        
        form.beginFieldSet("Sweep")
        form.addText("Sweep size", "sweepSize", task.sweepSize, fieldType="int")
        form.addBreak()
        form.endFieldSet()

        return form
    
    def onValidateValues(self, form):
        """
        Validate field values.
        """
        if form.getName() == "editJobForm":
        
            errorMessage = ""
            
            fieldValues = form.getFieldValues()
            
            if fieldValues["cpuTime"] == 0:
                fieldValues["cpuTime"] == 10
            elif fieldValues["cpuTime"] <1:
                fieldValues["cpuTime"] == 10
                                                    
            return errorMessage
        
        return ""
        
    def onAssignValues(self, task, form):
        """
        Assign field values.
        """
        
        if form.getName() == "editJobForm":
            
            formFields = form.getFieldValues()
            
            task.cpuTime = formFields["cpuTime"]
            task.notify = formFields["email"]
            task.sweepSize = formFields["sweepSize"]
            task.jobDescriptionString = formFields["jobDescriptionString"]
        
        return ""
    
    def onHandleUploadedFile(self, task, filename, fieldname):
        """
        Handle uploaded files.
        """

        if fieldname == "inputFile":
            task.addInputFile(filename)

    def onEditAfterCreate(self):
        """
        Return True to open edit page after creation.
        """
        return True

    def clearInputFiles(self):
        """
        Clear input files action.
        """
        task = self.getTask()
        task.clearInputFiles()
        self.redrawForm()
    
    def removeInputFiles(self):
        """
        Remove input files action.
        """
        task = self.getTask()
        
        removeFilename = self.getString(self.request(), "inputFiles")
        
        if removeFilename!="":
            task.removeInputFile(removeFilename)
            
        self.redrawForm()
