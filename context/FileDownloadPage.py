#
# FileDownloadPage
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

"""FileDownloadPage module"""

from Web.ApplicationSecurePage import ApplicationSecurePage

from MiscUtils.Funcs import uniqueId

import os, sys, string, types, time, mimetypes

from HyperText.HTML import *

import Lap
import Web
import Grid.ARC

class FileDownloadPage(ApplicationSecurePage):
	"""Page initiating a file download."""
	
	def title(self):
		"""Return page title."""
		return 'File view'

	def writeHTML(self):
		"""Render page."""
		
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
