from Web.DocViewPage import DocViewPage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocViewPage(DocViewPage):
					
	def onGetPageSource(self):
		return "users_guide.pdf"
		
	def onGetPluginName(self):
		return "DocUsersGuide"
	
	def onGetDocumentationTitle(self):
		return "Users Guide"

		

