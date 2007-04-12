from Web.DocSecurePage import DocSecurePage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocSecurePage(DocSecurePage):
					
	def onGetPageSource(self):
		return "getting_started.html"
		
	def onGetPluginName(self):
		return "DocGettingStarted"
		
	def onGetDocumentationTitle(self):
		return "Getting started"

