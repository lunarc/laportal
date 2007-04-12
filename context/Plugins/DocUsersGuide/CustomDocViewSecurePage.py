from Web.DocViewSecurePage import DocViewSecurePage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocViewSecurePage(DocViewSecurePage):
					
	def onGetPageSource(self):
		return "users_guide.pdf"
		
	def onGetPluginName(self):
		return "DocUsersGuide"
	
	def onGetDocumentationTitle(self):
		return "Users Guide"

		

