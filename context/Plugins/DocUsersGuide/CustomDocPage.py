from Web.DocPage import DocPage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocPage(DocPage):
					
	def onGetPageSource(self):
		return "users_guide.pdf"
		
	def onGetPluginName(self):
		return "DocUsersGuide"
	
	def onGetDocumentationTitle(self):
		return "Users Guide"

		

