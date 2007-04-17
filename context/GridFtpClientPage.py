#
# GridFtpClientPage
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

"""GridFtpClientPage module"""

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

class GridFtpClientPage(ApplicationSecurePage):
	"""Page implementing a simple gridftp client."""
	
	def actions(self):
		"""Return implemented actions."""
		return ApplicationSecurePage.actions(self) + ["openLocation"]
	
	def writeContent(self):
		"""Render page HTML."""
		# Get user information
		
		user = Lap.Session.User(self.session().value('authenticated_user'))
		userDir = user.getDir();
		
		if self.request().hasValue("dir"):
			changeDir = self.request().value("dir")
		else:
			changeDir = ""
			
		# Pop up view window
			
		if self.request().hasValue("idx"):
			self.writeln('<script language="javascript">')
			self.writeln('<!--')
			self.writeln('viewfileWindow = window.open("ViewGridFTPFilePage?idx='+self.request().field("idx")+'", "viewfileWindow", config="height=800,width=600, toolbar=no, menubar=no, scrollbars=yes, resizable=yes, location=no, status=no")')
			self.writeln('if (viewfileWindow.focus) {viewFileWindow.focus()}')
			self.writeln('-->')
			self.writeln('</script>')
		
		# Create user interface
		
		if self.session().hasValue("gridftp_url"):
			url = self.session().value("gridftp_url")
		else:
			url = ""
			
		if url!="" and changeDir!="":
			url = changeDir
			self.session().setValue("gridftp_url", url)
		
		form = Web.Ui.Form("gridFtpClient", self.pageLoc()+"/GridFtpClientPage", "GridFTP Client (Experimental)", "35em")
		form.setHaveButtonRow(False)
		
		form.addSubmitButton("Open location", "_action_openLocation")
		form.addSubmitButton("Add to bookmarks", "_action_addBookmarks")
		form.addSubmitButton("Bookmarks", "_action_bookmarks")
		form.addSeparator()
		form.addText("GridFTP URL", "url", url, "25em")
		
		form.render(self)
		
		# Render directory listing if any
		
		if url!="":

			# Get the ARC user interface
	
			ui = Grid.ARC.Ui(user)   
			resultVal, result = ui.ls(url)

			if self.session().hasValue("gridftpclient_urlList"):
				self.session().delValue("gridftpclient_urlList")
				
			if resultVal == 0:

				# Create output window
				
				self.session().setValue("gridftpclient_urlList", result)
				
				form = Web.Ui.TableForm("frmFileManager", "", "Directory contents", "35em", len(result)+2, 6)
				form.setAction("GridFtpClientPage")
				form.setHaveButtons(False)
				
				row = 0
				
				form.addNormalText(B("Type"), row, 0)
				form.addNormalText(B("File"), row, 1)
				form.addNormalText(B("Size"), row, 2)
				form.addNormalText(B("Last modified"), row, 3)
				form.addNormalText("", row, 4)
				form.addNormalText("", row, 5)
				
				row = row + 1
								
				splitURL = url.split("/")
				if len(splitURL)>3:
					upUrl = "/".join(splitURL[:-1])
									
					form.addNormalText(IMG(src="images/folder.gif"), row, 0)
					form.addNormalText(A("..", href="GridFtpClientPage?dir=%s" % upUrl), row, 1)
					form.addNormalText("", row, 2)
					form.addNormalText("", row, 3)
					form.addNormalText("", row, 4)
					form.addNormalText("", row, 5)
					
					row = row + 1
										
				idx = 0
			
				for entry in result:
					if entry[1] == "file":
						form.addNormalText(IMG(src="images/file.gif"), row, 0)
						form.addNormalText(A(entry[0], href="GridFtpClientPage?idx=%d" % idx), row, 1)
						form.addNormalText(A(IMG(src="images/file_view.gif", border=0), href="GridFtpClientPage?idx=%d" % idx), row, 4)
						form.addNormalText(A(IMG(src="images/file_download.gif", border=0), href="FileDownloadGridFTPPage?idx=%d" % idx), row, 5)
					else:
						form.addNormalText(IMG(src="images/folder.gif"), row, 0)
						form.addNormalText(A(entry[0], href="GridFtpClientPage?dir=%s" % url+"/"+entry[0]), row, 1)
						form.addNormalText("", row, 4)
						form.addNormalText("", row, 5)

						
					idx = idx + 1
											
					form.addNormalText(entry[2], row, 2)
					form.addNormalText(entry[3], row, 3)					
					
					row = row + 1
					
					
				form.render(self)
			else:
				window = Web.Ui.Window("Error")
				body = window.getBody()
				for row in result:
					body.append(P(row+"<br>"))
				window.render(self);
					
			
		
	def openLocation(self):
		"""Open location URL."""
		
		url = self.getURLString(self.request(), "url")
		
		if url != None:
			self.session().setValue("gridftp_url", url)
		else:
			self.session().setValue("gridftp_url", "")
			
		self.writeBody()

