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

class ViewFilePage(ApplicationSecurePage):
	
	def title(self):
		return 'File view'
			
	def writeHTML(self):
		filename = self.getPageProperty("ViewFilesPage", "viewfile_filename")
		response = self.response()
		
		(mtype,enctype) = mimetypes.guess_type(filename)
		
		if mtype==None:
			mtype = "text/plain"
		
		fd = open(filename)

		response.setHeader('Content-Type',mtype)
		response.flush()

		# Get user information
	
		mode = ""
		jobName = ""
		viewMode = ""
		filename = ""
		
		chunksize = response.streamOut().bufferSize()
		outchunk = fd.read(chunksize)
		while outchunk:
			self.write(outchunk)
			outchunk = fd.read(chunksize)
			
		fd.close()
		
		self.session().setValue("viewfile_filename", "")
					
					
					