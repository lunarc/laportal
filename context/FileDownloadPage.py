from Web.ApplicationSecurePage import ApplicationSecurePage

from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes

from HyperText.HTML import *

import Lap
import Web
import Grid.ARC

class FileDownloadPage(ApplicationSecurePage):
	def title(self):
		return 'File view'

	def writeHTML(self):
		
		fileEntry = self.session().value("ViewFilesPage_downloadfile")
		
		response = self.response()
		
		(mtype,enctype) = mimetypes.guess_type(fileEntry)
		
		#if mtype==None:
		mtype = "application/force-download"
		
		fd = open(fileEntry)

		response.setHeader('Content-Type',mtype)
		response.setHeader('Content-Disposition','attachment; filename="%s"' % os.path.basename(fileEntry))
		response.setHeader('Content-Length','%d' % os.path.getsize(fileEntry))
		response.flush()

		chunksize = response.streamOut().bufferSize()
		outchunk = fd.read(chunksize)
		while outchunk:
			self.write(outchunk)
			outchunk = fd.read(chunksize)

		print "downloadFile() done."
