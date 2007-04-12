from Web.DocSecurePage import DocSecurePage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocSecurePage(DocSecurePage):
					
	def onGetPageSource(self):
		return "programming_guide.html"
		
	def onGetPluginName(self):
		return "DocProgrammingGuide"
		
	def onGetDocumentationTitle(self):
		return "Programming Guide"

