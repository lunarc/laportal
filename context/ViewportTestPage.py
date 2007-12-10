#
# VOPage base class module
#
# Copyright (C) 2007 Jonas Lindemann
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

"""VOPage class module"""

from Web.ApplicationSecurePage import ApplicationSecurePage
from time import *

import os
import sys
import string
import pickle

import Lap
import Lap.Session

import Web
import Web.Ui
import Web.UiExt
import Web.Dialogs

class ViewportTestPage(ApplicationSecurePage):
	"""VOPage base class
	
	This base class is the base for any VO plugins. The class implements
	a generic VO joining request."""
	
	# ----------------------------------------------------------------------
	# Private methods
	# ----------------------------------------------------------------------	

	# ----------------------------------------------------------------------
	# Get/set methods
	# ----------------------------------------------------------------------
	
	def setReturnPage(self, returnPage):
		adapterName = self.request().adapterName()
		self._returnPage = "%s/context/" % returnPage
		
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			

	def onInit(self, adapterName):
		
		panel1 = Web.UiExt.Panel(self, 'panel1')
		panel1.region = 'center'
		panel1.contentEl = 'center1'
		panel1.margins = '0 0 0 0'
		
		panel2 = Web.UiExt.Panel(self, 'panel2')
		panel2.region = 'west'
		panel2.contentEl = 'center2'
		panel2.margins = '0 0 0 0'
		
		viewport = Web.UiExt.Viewport(self, 'viewport')
		viewport.add(panel1)
		viewport.add(panel2)
		
		self.addControl("viewport", viewport)
		
	def onUseMenu(self):
		return True

	# ----------------------------------------------------------------------
	# Form action methods
	# ----------------------------------------------------------------------
		