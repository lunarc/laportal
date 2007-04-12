from Web.DocSecurePage import DocSecurePage

import Web
import Web.Ui
import Web.Dialogs

class CustomDocSecurePage(DocSecurePage):
					
	def onGetPageSource(self):
		return "users_guide.html"
		
	def onGetPluginName(self):
		return "DocUsersGuide"
		
	def onGetDocumentationTitle(self):
		return "User's Guide"

