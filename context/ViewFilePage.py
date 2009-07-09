#
# ViewFilePage
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

"""ViewFilePage module"""

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
	"""Page for displaying job result files.
	
	The page tries to guess the mime type of the file, when it can't determine
	the type it uses text/plain.
	
	The page uses the property, viewfile_filename, from the ViewFilesPage
	to determine what file to display."""
	
	def title(self):
		"""Return page title"""
		return 'File view'
			
	def writeHTML(self):
		"""Render page html"""
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
					
					
					