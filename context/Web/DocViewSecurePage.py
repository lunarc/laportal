#
# DocViewPage base class module
#
# Copyright (C) 2006 Jonas Lindemann
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

"""DocViewSecurePage module"""

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

class DocViewSecurePage(ApplicationSecurePage):
	"""Class for viewing generic documentation (secure pages)
	
	This class tries to guess the contents type of provided document and
	display it with the correct Content-Type tag. This enables PDF-files
	to be displayed in a separate window."""
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------				
	
	def title(self):
		"""Render page title."""
		return self.onGetDocumentationTitle()	
				
	def writeHTML(self):
		"""Render page."""
			
		pluginName = self.onGetPluginName()
		pageSource = self.onGetPageSource()

		filename = self.contextDir()+"/Plugins/%s/%s" % (pluginName, pageSource)
		
		response = self.response()
		
		(mtype,enctype) = mimetypes.guess_type(filename)
		
		print mtype, ", ", enctype
		
		if mtype==None:
			mtype = "text/plain"
		
		fd = open(filename)

		response.setHeader('Content-Type',mtype)
		response.flush()

		chunksize = response.streamOut().bufferSize()
		outchunk = fd.read(chunksize)
		while outchunk:
			self.write(outchunk)
			outchunk = fd.read(chunksize)
			
		fd.close()
        
	# ----------------------------------------------------------------------
	# DocViewPage Event methods (Callbacks)
	# ----------------------------------------------------------------------								

	def onGetDocumentationTitle(self):
		"""Override to return the page title."""
		return "Non customised title."
	
	def onGetPluginName(self):
		"""Override to provide the correct plugin name."""
		return "DocViewPage"
		
	def onGetPageSource(self):
		"""Return the source of the page."""
		return ""
