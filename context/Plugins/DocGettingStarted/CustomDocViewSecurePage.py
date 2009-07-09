from Web.DocViewSecurePage import DocViewSecurePage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocViewSecurePage(DocViewSecurePage):
					
	def onGetPageSource(self):
		return "getting_started.pdf"
		
	def onGetPluginName(self):
		return "DocGettingStarted"
	
	def onGetDocumentationTitle(self):
		return "Getting Started"

		

