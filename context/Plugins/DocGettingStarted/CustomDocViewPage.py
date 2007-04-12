from Web.DocViewPage import DocViewPage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocViewPage(DocViewPage):
					
	def onGetPageSource(self):
		return "getting_started.pdf"
		
	def onGetPluginName(self):
		return "DocGettingStarted"
	
	def onGetDocumentationTitle(self):
		return "Getting Started"

		

