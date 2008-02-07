from Web.ApplicationPage import ApplicationPage

from HyperText.HTML import *

class MenuTestPage(ApplicationPage):

	def title(self):
		return 'Welcome!'

	def onUseAlternateMenu(self):
		return True
