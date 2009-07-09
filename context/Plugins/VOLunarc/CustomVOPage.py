from Web.VOPage import VOPage

import Lap

from Plugins.VOLunarc.CustomVO import CustomVO

pluginName = "VOLunarc"

class CustomVOPage(VOPage):
	
	def onGetPageAddress(self):
		return self.pageLoc()+"/Plugins/%s/CustomVOPage" % (pluginName)
	
	def onFinishPageName(self):
		return self.pageLoc()+"/SecureWelcomePage"

	def onReturnPageName(self):
		return self.pageLoc()+"/Plugins/%s/CustomVOPage" % (pluginName)
	
	def onCreateVO(self):
		"""Create the derived vo class and return it to the parent class."""
	
		vo = CustomVO()
		return vo
		
