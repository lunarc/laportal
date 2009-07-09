#
# ViewGridFTPFilePage
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

"""ViewGridFTPFilePage module"""

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

class ViewGridFTPFilePage(ApplicationSecurePage):
	"""Page for displaying content of GridFTP files.
	
	The page tries to guess the correct mime type, if not found
	text/plain will be used."""
	
	def title(self):
		return 'File view'
			
	def writeHTML(self):
		
		user = Lap.Session.User(self.session().value('authenticated_user'))		
		ui = Grid.ARC.Ui(user)   
			
		urlIdx = int(self.request().field("idx"))
		urlList = self.getSessionValue("gridftpclient_urlList")
		
		url = self.session().value("gridftp_url")+"/"+urlList[urlIdx][0]
		
		response = self.response()
		
		(mtype,enctype) = mimetypes.guess_type(os.path.basename(url))
		
		print "basename=",os.path.basename(url)
		print "mtype=",mtype
		print "enctype=",enctype
				
		if mtype==None:
			mtype = "text/plain"

		ftpFile = ui.pcopy(url)
		
		if mtype!="force/download":
			response.setHeader('Content-Type',mtype)
		else:
			response.setHeader('Content-Type',mtype)
			response.setHeader('Content-Disposition','attachment; filename="%s"' % os.path.basename(url))
			response.setHeader('Content-Length','%d' % int(urlList[urlIdx][2]))
			
		response.flush()

		# Get user information
	
		mode = ""
		jobName = ""
		viewMode = ""
		filename = ""
		
		chunksize = response.streamOut().bufferSize()
		outchunk = ftpFile.read(chunksize)
		while outchunk:
			self.write(outchunk)
			outchunk = ftpFile.read(chunksize)
			
		ftpFile.close()
		
		self.session().setValue("viewfile_filename", "")
						