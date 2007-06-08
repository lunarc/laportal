from WebKit.Page import Page

from HyperText.HTML import *



class MenuTestPage(Page):

	def title(self):
		return 'Welcome!'
	
	def writeHeadParts(self):
		self.writeTitle()
		self.writeStyleSheet()
		self.writeScripts()
		
	def writeStyleSheet(self):
		wr = self.writeln
		wr('<link rel="stylesheet" type="text/css" href="../resources/css/ext-all.css"/>')
		
	def writeScripts(self):
		wr = self.writeln
		wr('<script type="text/javascript" src="/ext/adapter/yui/yui-utilities.js"></script>')
		wr('<script type="text/javascript" src="/ext/adapter/yui/ext-yui-adapter.js"></script>')
		wr('<script type="text/javascript" src="ext/ext-all.js"></script>')
	
	def writeContent(self):
		self.writeln("Hello, world!")
