from Web.DocPage import DocPage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocPage(DocPage):
					
	def onGetPageSource(self):
		return "programming_guide.html"
		
	def onGetPluginName(self):
		return "DocProgrammingGuide"
	
	def onGetDocumentationTitle(self):
		return "Programming Guide"

		

