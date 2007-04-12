from Web.DocPage import DocPage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocPage(DocPage):
					
	def onGetPageSource(self):
		return "getting_started.html"
		
	def onGetPluginName(self):
		return "DocGettingStarted"
	
	def onGetDocumentationTitle(self):
		return "Getting started"

		

