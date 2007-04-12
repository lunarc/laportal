from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId
import string, types

import Grid.ARC
import Lap.Session


class SyncJobsPage(ApplicationSecurePage):
	def title(self):
		return 'Syncronising jobs'

	def writeContent(self):
		user = Lap.Session.User(self.session().value('authenticated_user'))
		ui = Grid.ARC.Ui(user)
		
		ui.sync()
		
		self.sendRedirectAndEnd("ManageGridJobPage")

