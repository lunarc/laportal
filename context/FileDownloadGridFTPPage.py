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

class FileDownloadGridFTPPage(ApplicationSecurePage):
	
	def title(self):
		return 'File view'
			
	def writeHTML(self):
		
		user = Lap.Session.User(self.session().value('authenticated_user'))		
		ui = Grid.ARC.Ui(user)   
			
		urlIdx = int(self.request().field("idx"))
		urlList = self.getSessionValue("gridftpclient_urlList")
		
		url = self.session().value("gridftp_url")+"/"+urlList[urlIdx][0]
		
		response = self.response()
		
		mtype = "force/download"

		ftpFile = ui.pcopy(url)
		
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
						