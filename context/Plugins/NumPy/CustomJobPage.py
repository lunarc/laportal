#
# LAP Matlab Single Plugin - Version 0.9
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

from Web.JobPage import JobBasePage
from time import *
import os
import sys
import pwd
import string
import pickle

import Grid.ARC

import Lap
import Web
import Plugins.NumPy.CustomJob
import Lap.Utils

pluginName = "NumPy"

class CustomJobPage(JobBasePage):
    
    def actions(self):
        return JobBasePage.actions(self) + ["clearPackageFiles", "clearExtraFiles",
                                        "removePackageFiles", "removeExtraFiles" ]

    def onInitPage(self):
        tabControl = Web.Ui.jQueryTabs(self)
        tabControl.name = "tabs"
        self.addControl(tabControl)
    
    def onGetPageAddress(self):
        return self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName)
    
    def onGetFileTransferFields(self):
        return ["mainFile", "packageFile", "extraFile"]

    def onCreateNewTask(self):
        """Create the derived task class and return it to the parent class."""
    
        task = Plugins.NumPy.CustomJob.CustomTask()
        task.taskEditPage = "/Plugins/%s/CustomJobPage" % pluginName
        return task

    def onCreateEditJobForm(self, task):
        """Create the form used when editing an existing job definition
        is created."""
    
        form = Web.Ui.Form("editJobForm", self.pageLoc()+"/Plugins/%s/CustomJobPage" % (pluginName), "Edit NumPy job", width="35em")
        
        #attribs = task.getAttributes()
        #xrslAttribs = task.getXRSLAttributes()
        
        form.beginFieldSet("Packages")
        form.beginSelect("Package files", "packageFiles", size=4, width="20em")
        for package in task.packages:
            print "Adding package."
            form.addOption(package)
        form.endSelect()
        form.addBreak()
        form.addFile("Add package file(s) (*.zip)", "packageFile", "")
        form.addBreak()
        form.addBreak()
        form.beginIndent("9.0em")
        form.addSubmitButton("Upload", "_action_uploadFile")
        form.addSubmitButton("Clear", "_action_clearPackageFiles")
        form.addSubmitButton("Remove", "_action_removePackageFiles")
        form.endIndent()
        form.endFieldSet()
        
        form.beginFieldSet("Extra files")
        form.beginSelect("Additional files", "extraFiles", size=4, width="20em")
        for extraFile in task.extraFiles:
            form.addOption(extraFile)
        form.endSelect()
        form.addBreak()
        form.addFile("Add additional file(s)", "extraFile", "")
        form.addBreak()
        form.addBreak()
        form.beginIndent("9.0em")
        form.addSubmitButton("Upload", "_action_uploadFile")
        form.addSubmitButton("Clear", "_action_clearExtraFiles")
        form.addSubmitButton("Remove", "_action_removeExtraFiles")
        form.endIndent()
        form.endFieldSet()

        form.beginFieldSet("Main file")
        form.addFile("Main file", "mainFile", "")
        form.addBreak()
        form.beginIndent("9.0em")
        form.addSubmitButton("Upload", "_action_uploadFile")
        form.endIndent()
        form.addBreak()
        form.addReadonlyText("Current file", "prevFile", task.mainFile)
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
        
        print "onAssignValues() - ", form.getName()
        
        if form.getName() == "editJobForm":
            
            formFields = form.getFieldValues()
            
            task.cpuTime = formFields["cpuTime"]
            task.notify = formFields["email"]
            task.sweepSize = formFields["sweepSize"]
            
            print "sweepSize = ", task.sweepSize
        
        return ""

                    
    def onHandleUploadedFile(self, task, filename, fieldname):
        """Special handling for uploaded files."""

        if fieldname == "mainFile":
            task.mainFile = filename
            
        if fieldname == "packageFile":
            task.addPackage(filename)
            
        if fieldname == "extraFile":
            task.addExtraFile(filename)
            
    def onEditAfterCreate(self):
        return True
    
    def clearPackageFiles(self):
        task = self.getTask()
        task.clearPackages()
        self.redrawForm()
    
    def removePackageFiles(self):
        task = self.getTask()
        
        removeFilename = self.getString(self.request(), "packageFiles")
        
        if removeFilename!="":
            task.removePackage(removeFilename)
            
        self.redrawForm()
    
    def clearExtraFiles(self):
        task = self.getTask()
        task.clearExtraFiles()
        self.redrawForm()
    
    def removeExtraFiles(self):
        task = self.getTask()
        
        print self.request().fields()
        
        removeFilename = self.getString(self.request(), "extraFiles")
        
        if removeFilename!="":
            task.removeExtraFile(removeFilename)
            
        self.redrawForm()
