#
# ViewFilesPage
#
# Copyright (C) 2006-2007 Jonas Lindemann
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

"""ViewFilesPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes, shutil

from HyperText.HTML import *

import Grid.ARC

import Lap
import Lap.Session
import Lap.Utils

import Web
import Web.Ui
import Web.Dialogs

class ViewFilesPage(ApplicationSecurePage):
	"""File manager page for downloaded job files.
	
	This page is designed to display downloaded session directories for
	a specific job. The page is the called with mode=session and jobname set to
	the job to display downloaded results for. The syntax is:
	
	.../ViewFilesPage?mode=session&jobname={jobname}
	
	The page has additional request parameters, but these are only used internally.
	"""
	
	def title(self):
		"""Return page title."""
		return 'File view'

	def writeContent(self):
		"""Render the page HTML."""
			
		if self.hasProperty("status"):

			# Show any form message boxes
			
			if self.getProperty("status")<>"":
				Web.Dialogs.messageBox(self, self.getProperty("status"), "Message", "ViewFilesPage")

			sefl.delProperty("status")
			
		elif self.hasProperty("confirm"):
			
			# Show form confirmation dialogs
			
			Web.Dialogs.messageBoxYesNo(self,
								self.getProperty("confirmMessage"),
								self.getProperty("confirmTitle"),
								"_action_deleteDirYes",
								"_action_deleteDirNo"
								)
			
			self.delProperty("confirmMessage")
			self.delProperty("confirmTitle")
			self.delProperty("confirmNoPage")
			self.delProperty("confirmYesPage")			
			
		else:
		
			# Get user information
		
			user = Lap.Session.User(self.session().value('authenticated_user'))
			userDir = user.getDir();
			
			mode = ""
			jobName = ""
			viewMode = ""
			sessionDir = ""
			fileEntry = ""
			dirEntry = ""
			currentDir = ""
			changeDir = ""
			topDir = ""
			
			# Session state information
			
			if self.hasProperty("mode"):
				viewMode = self.getProperty("mode")
				
			if self.hasProperty("jobname"):
				jobName = self.getProperty("jobname")
				
			if self.hasProperty("dir"):
				dirEntry = self.getProperty("dir")
				
			if self.hasProperty("sessiondir"):
				sessionDir = self.getProperty("sessiondir")
				
			if self.hasProperty("dir"):
				dirEntry = self.getProperty("dir")
				
			if self.hasProperty("dirTop"):
				topDir = self.getProperty("dirTop")
				
			# Handle the request case of this page
				
			if self.request().hasValue("mode"):
				viewMode = self.getStringNoDoubleDot(self.request(),"mode")
				self.setProperty("mode", viewMode)
				
			if self.request().hasValue("jobname"):
				jobName = self.getStringNoDoubleDot(self.request(),"jobname")
				self.setProperty("jobname", jobName)
				
			if self.request().hasValue("sessiondir"):
				sessionDir = self.getStringNoDoubleDot(self.request(),"sessiondir")
				self.setProperty("sessiondir", sessionDir)
				
			if self.request().hasValue("fileentry"):
				fileEntry = self.getStringNoDoubleDot(self.request(), "fileentry")
				self.setProperty("entry", fileEntry)
				
			if self.request().hasValue("direntry"):
				changeDir = self.getStringNoDoubleDot(self.request(), "direntry")
				
			if viewMode == "view":
				
				if fileEntry!="":
							
					jobDir = os.path.join(userDir, "job_%s" % jobName)
					
					filename = os.path.join(os.path.join(jobDir,dirEntry), fileEntry)
					
					self.setProperty("viewfile_filename", filename)
					
					# Open a popup window
					
					self.writeln('<script language="javascript">')
					self.writeln('<!--')
					self.writeln('viewfileWindow = window.open("ViewFilePage", "viewfileWindow", config="height=800,width=600, toolbar=no, menubar=no, scrollbars=yes, resizable=yes, location=no, status=no")')
					self.writeln('if (viewfileWindow.focus) {viewFileWindow.focus()}')
					self.writeln('-->')
					self.writeln('</script>')
					
					# Return to file mode again
					
					self.setProperty("mode", "file")					
					viewMode = "file"
										
				elif dirEntry!="":
					
					print 'dirEntry!=""'
					
					dirEntry = os.path.join(dirEntry, changeDir)
					self.setProperty("dir", dirEntry)
					
					self.setProperty("mode", "file")					
					viewMode = "file"
	
			if viewMode == "file":
				
				jobDir = os.path.join(userDir, "job_%s" % jobName)
				
				browseDir = os.path.join(jobDir, dirEntry)
				fileList, dirList = Lap.Utils.listFilesAndDirectories(browseDir)
									
				# Check for files
				
				if len(fileList)==0 and len(dirList)==0:
					Web.Dialogs.messageBox(self, "No files to display", "View files", "ManageJobPage")
					return
	
				# Create form for viewing session directories
				
				form = Web.Ui.TableForm("frmFileManager", "", "Downloaded job files", "40em", len(dirList)+len(fileList)+1, 6)
				form.setAction("ViewFilesPage")
				
				row = 0
				
				form.addNormalText(B("Type"), row, 0)
				form.addNormalText(B("File"), row, 1)
				form.addNormalText(B("Size"), row, 2)
				form.addNormalText(B("Last modified"), row, 3)
				form.addNormalText("", row, 4)
				form.addNormalText("", row, 5)
				
				row = row + 1 
				
				for dirEntry in dirList:
					form.addNormalText(IMG(src="images/folder.gif"), row, 0)
					form.addNormalText(A(dirEntry[0], href=self.pageLoc()+"/ViewFilesPage?mode=view&direntry="+dirEntry[0]), row, 1)
					form.addNormalText(dirEntry[3], row, 2)
					#form.addNormalText(time.asctime(time.localtime(dirEntry[1])), row, 4)
					form.addNormalText(time.asctime(time.localtime(dirEntry[2])), row, 3)
					form.addNormalText("", row, 4)
					form.addNormalText("", row, 5)
					row = row + 1
					
				for fileEntry in fileList:
					form.addNormalText(IMG(src="images/file.gif"), row, 0)
					form.addNormalText(A(fileEntry[0], href=self.pageLoc()+"/ViewFilesPage?mode=view&fileentry="+fileEntry[0]), row, 1)
					form.addNormalText(fileEntry[3], row, 2)
					#form.addNormalText(time.asctime(time.localtime(fileEntry[1])), row, 4)
					form.addNormalText(time.asctime(time.localtime(fileEntry[2])), row, 3)
					form.addNormalText(A(IMG(src="images/file_view.gif", border=0), href=self.pageLoc()+"/ViewFilesPage?mode=view&fileentry="+fileEntry[0]), row, 4)
					form.addNormalText(A(IMG(src="images/file_download.gif", border=0), href=self.pageLoc()+"/ViewFilesPage?mode=download&fileentry="+fileEntry[0]), row, 5)
					row = row + 1

				form.addFormButton("Download all (tar.gz)", "_action_downloadAll")
				form.addFormButton("Back", "_action_goBack")
				
				form.setHaveSubmit(False)
					
				form.render(self)
				
			if viewMode == "download":

				filename = os.path.join(dirEntry, fileEntry)
				
				self.setProperty("downloadfile", filename)
				self.forward("FileDownloadPage")
						
			if viewMode == "session":
				
				# Get job directory
	
				jobDir = os.path.join(userDir, "job_%s" % jobName)
				
				# Check for session directories
				
				sessionDirs = []
				
				for entry in os.listdir(jobDir):
					if os.path.isdir(os.path.join(jobDir,entry)):
						atime = os.path.getatime(os.path.join(jobDir,entry))
						mtime = os.path.getmtime(os.path.join(jobDir,entry))
						sessionDirs.append((entry, atime, mtime))
						
				if len(sessionDirs)==0:
					Web.Dialogs.messageBox(self, "No downloaded results to display", "View files", "ManageJobPage")
					return
				
				# Intialise file viewing
				
				self.setProperty("dir", jobDir)
				self.setProperty("dirTop", jobDir)
	
				# Create form for viewing session directories
				
				form = Web.Ui.TableForm("frmFileManager", "", "Downloaded job files", "40em", len(sessionDirs)+1, 5)
				form.setAction("ViewFilesPage")
				
				row = 0
				
				form.addNormalText("", row, 0)
				form.addNormalText(B("JobID"), row, 1)
				#form.addNormalText(B("Last accessed"), row, 2)
				form.addNormalText(B("Last modified"), row, 2)
				form.addNormalText(B("View results"), row, 3)
				form.addNormalText(B("View files"), row, 4)

				
				row = row + 1 
				
				for sessionDir in sessionDirs:
					form.addCheck("", "chkDir", sessionDir[0], row, 0)
					form.addNormalText(A(sessionDir[0],href=self.pageLoc()+"/ViewFilesPage?mode=view&direntry="+sessionDir[0]), row, 1)
					form.addNormalText(time.asctime(time.localtime(sessionDir[2])), row, 2)
					form.addNormalText(CENTER(IMG(src="images/results.gif")), row, 3)
					form.addNormalText(CENTER(A(IMG(src="images/folder.gif", border=0), href=self.pageLoc()+"/ViewFilesPage?mode=view&direntry="+sessionDir[0])), row, 4)
					row = row + 1
				
				form.addFormButton("Delete", "_action_deleteDir")
				form.addFormButton("Back", "_action_goBack")
				
				form.setHaveSubmit(False)
					
				form.render(self)
	
	def deleteDir(self):
		"""Delete checked directory (action).
		
		Displays a verification dialog before permanently removing the
		directory."""
		
		if self.request().hasValue("chkDir"):
			self.confirm("Are you sure?", "Delete directory", "", "")
			self.setProperty("deletedir", self.request().value("chkDir"))
			self.writeBody()
		else:
			self.setFormStatus("A job must be selected.")
			self.writeBody()
	
	def downloadAll(self):
		"""Download all displayed files as a tarball (action)."""
		
		jobName = self.getProperty("jobname")
		currentDir = self.getProperty("dir")
		
		filename = "%s_%s" % (jobName, os.path.basename(currentDir))
		
		#oldDir = os.getcwd()
		#os.chdir(currentDir+"/..")
		os.system('cd "%s/..";tar cvzf /tmp/%s.tar.gz %s' % (currentDir, filename, os.path.basename(currentDir)))
		#os.chdir(oldDir)
		
		fullFilename = "/tmp/"+filename + ".tar.gz"
		
		self.setProperty("downloadfile", fullFilename)
		self.forward("FileDownloadPage")

	def goBack(self):
		"""Goto previous directory / session (action)."""
		
		viewMode = self.getProperty("mode")
		
		if viewMode == "session":
			self.sendRedirectAndEnd("ManageJobPage")
			return
		
		if viewMode == "file":
			
			topDir = self.getProperty("dirTop")
			
			orgDir = self.getProperty("dir")
			newDir = os.path.dirname(orgDir)
			
			if newDir!=topDir:
				self.setProperty("mode", "file")
				self.setProperty("dir", newDir)
			else:
				self.setProperty("mode", "session")
				self.setProperty("dir", "")
				
			self.writeBody()
			
		if viewMode == "view":
			self.setProperty("mode", "file")
			
			self.writeBody()

	def showOutput(self):
		pass

	def showErrors(self):
		pass

	def viewResults(self):
		pass
			
	def actions(self):
		"""Return implemented actions."""
		return ApplicationSecurePage.actions(self) + ["deleteDir", 
			"downloadAll", "goBack", "deleteDirYes", "deleteDirNo",
			"showOutput", "showErrors"]
	
	def deleteDirYes(self):
		"""Really delete checked directory.
		
		This function is called by the verification dialog in response
		to a yes answer."""

		if self.hasProperty("deletedir"):
			
			deleteDirs = self.getProperty("deletedir")
			
			if len(deleteDirs)==0:
				return
			
			if type(deleteDirs) is str:
				deleteDirs = [deleteDirs]
			
			sefl.delProperty("deletedir")
			
			# Get user dir

			user = Lap.Session.User(self.getProperty('authenticated_user'))
			userDir = user.getDir();

			if self.hasProperty("jobname"):
				jobName = self.getProperty("jobname")

			for sessionDir in deleteDirs:
			
				jobDir = os.path.join(userDir, "job_%s" % jobName)
	
				deleteDir = os.path.join(jobDir, sessionDir)	
					
				print "deleteDirYes:", os.path.join(jobDir,sessionDir)
				
				# Delete job directory
				
				shutil.rmtree(deleteDir, True)
			
			self.writeBody()
	
	def deleteDirNo(self):
		"""Cancel directory removal.
		
		This action is called by the No button of the
		verification dialog."""
		
		if self.hasProperty("deletedir"):
			sefl.delProperty("deletedir")
		self.writeBody()
		
	def setFormStatus(self, status):
		"""Set the form status text message.
		
		If not empty a message is displayed when the page is re-rendered."""
		self.setProperty("status", status)
		
	def confirm(self, question, title, yesPage, noPage):
		"""Set properties for a confirmation dialog.
		
		When the page is re-rendered a confirmation dialog is displayed."""
		
		self.setProperty("confirmMessage", question)
		self.setProperty("confirmTitle", title)
		self.setProperty("confirmYesPage", yesPage)
		self.setProperty("confirmNoPage", noPage)



