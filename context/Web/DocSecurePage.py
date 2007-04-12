#
# DocSecurePage base class module
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

"""DocSecurePage module"""

from Web.SecurePage import SecurePage

import Web
import Web.Ui
import Web.Dialogs

from HyperText.HTML import *

from sgmllib import SGMLParser

class BaseHTMLProcessor(SGMLParser):
	"""Customised class for extracting the basic structure of
	a HTML document for use in documentation pages."""	
	def reset(self):        
		self._addPieces = False                
		self.pieces = []
		SGMLParser.reset(self)
		
	def appendPiece(self, data):
		if self._addPieces:
			self.pieces.append(data)
			
	def startAppend(self):
		self._addPieces = True
		
	def stopAppend(self):
		self._addPieces = False
			
	def unknown_starttag(self, tag, attrs): 
		strattrs = "".join([' %s="%s"' % (key, value) for key, value in attrs])
		self.appendPiece("<%(tag)s%(strattrs)s>" % locals())
		if tag == "body":
			self.startAppend()

	def unknown_endtag(self, tag):          
		if tag == "body":
			self.stopAppend()
		self.appendPiece("</%(tag)s>" % locals())

	def handle_charref(self, ref):          
		self.appendPiece("&#%(ref)s;" % locals())

	def handle_entityref(self, ref):        
		self.appendPiece("&%(ref)s;" % locals())
		#if htmlentitydefs.entitydefs.has_key(ref):
		#	self.appendPiece(";")

	def handle_data(self, text):            
		self.appendPiece(text)

	def handle_comment(self, text):         
		self.appendPiece("<!--%(text)s-->" % locals())

	def handle_pi(self, text):              
		self.appendPiece("<?%(text)s>" % locals())

	def handle_decl(self, text):
		self.appendPiece("<!%(text)s>" % locals())
		
	def output(self):
		"""Return processed HTML as a single string"""
		return "".join(self.pieces) 
		

class DocSecurePage(SecurePage):
	"""HTML documentation page class (secure pages)
	
	Extracts the basic structure of a provided HTML file and adapts
	it to the application portal documentation structure. This class is
	not to be used directly, instead a derived class should be created
	overriding the neccesary callbacks:
	
	onGetDocumentationTitle() - Document title.
	onGetPluginName() - Name of the plugin.
	onGetPageSource() - Source of the html document.
	onGetPageWidth() - Width of the documentation window."""
	
	# ----------------------------------------------------------------------
	# Overidden methods (WebKit)
	# ----------------------------------------------------------------------			

	def title(self):
		"""Return page title"""
		
		return self.onGetDocumentationTitle()	
	
	def writeContent(self):
		"""Render documetation page."""
	
		pluginName = self.onGetPluginName()
		pageSource = self.onGetPageSource()
		pageWidth = self.onGetPageWidth()

		contentPageURL = self.pageLoc()+"/Plugins/%s/%s" % (pluginName, pageSource)
		
		docFile = file(self.contextDir()+"/Plugins/%s/%s" % (pluginName, pageSource), "r")
		content = docFile.read()
		docFile.close()
	
		bodyParser = BaseHTMLProcessor()
		bodyParser.feed(content)
		bodyParser.close()
		
		self.writeln('<DIV id="doctoolbar">')
		self.writeln(self.onGetDocumentationTitle())
		self.writeln('</DIV>')		
		
		self.writeln('<DIV id="docarea">')
		self.write(bodyParser.output())
		self.writeln('</DIV>')

	# ----------------------------------------------------------------------
	# DocPage Event methods (Callbacks)
	# ----------------------------------------------------------------------								
	
	def onGetDocumentationTitle(self):
		"""Return documentation title."""
		return "Non customised title."
	
	def onGetPluginName(self):
		"""Return plugin name."""
		return "DocSecurePage"
		
	def onGetPageSource(self):
		"""Return documentation source file."""
		return ""
			
	# ----------------------------------------------------------------------
	# DefaultPage Event methods (Callbacks)
	# ----------------------------------------------------------------------								

	def onUseMenu(self):
		"""Don't use menu."""
		return False
	
	def onUseTooltips(self):
		"""No tooltips."""
		return False
	
	def onUseLogo(self):
		"""No logo."""
		return False
	
	def onUseContentDiv(self):
		"""No content div."""
		return False

	def onIncludeLapCSS(self):
		"""Don't include LAP CSS file."""
		return False

	def onIncludeUiCSS(self):
		"""Don't include user interface CSS file."""
		return False

	def onIncludeMenuCSS(self):
		"""Don't include menu CSS file."""
		return False

	def onIncludeMenuJavaScript(self):
		"""Don't include any javascript."""
		return False

	def onAdditionalCSS(self):
		"""Add additional CSS file."""
		return ["/css/doc.css"]
		
		
		
		
