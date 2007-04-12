from Web.ApplicationSecurePage import ApplicationSecurePage
from MiscUtils.Funcs import uniqueId
import string, types, time

jobRunningColor   = "51, 204, 0"
jobQueuingColor   = "255, 204, 0"
jobAcceptedColor  = "0, 204, 204"
jobDeletedColor   = "204, 0, 0"
jobFinishingColor = "51, 204, 0"
jobFinishedColor  = "51, 204, 0"

import Web.Dialogs
import Web.Ui
import Lap.Session
import Grid.ARC

class JobStatusPage(ApplicationSecurePage):
	def title(self):
		return 'Job status'

	def writeContent(self):
		user = Lap.Session.User(self.session().value('authenticated_user'))
		ui = Grid.ARC.Ui(user)
		jobs = ui.jobStatus()
		
		if jobs==None:
			Web.Dialogs.messageBox(self, "grid-proxy is about to expire please create a new proxy.", "Manage running jobs")
		else:

			table = Web.Ui.Table(len(jobs)+1,4)
			table.setItem(0, 0, "ID")
			table.setItem(0, 1, "Name")
			table.setItem(0, 2, "Status")
			table.setItem(0, 3, "Error")
	
			row = 1		
	
			for key in jobs.keys():
				table.setItem(row,0,key)
				table.setItem(row,1,jobs[key]["name"])
				if jobs[key]["status"] == "INLRMS: Q":
					table.setColor(row,2, jobQueuingColor)
				if jobs[key]["status"] == "INLRMS: wait":
					table.setColor(row,2, jobQueuingColor)
				if jobs[key]["status"] == "INLRMS: R":
					table.setColor(row,2, jobRunningColor)
				if jobs[key]["status"] == "ACCEPTED":
					table.setColor(row,2, jobAcceptedColor)
				if jobs[key]["status"] == "DELETED":
					table.setColor(row,2, jobDeletedColor)
				if jobs[key]["status"] == "FINISHING":
					table.setColor(row,2, jobFinishingColor)
				if jobs[key]["status"][0:8] == "FINISHED":
					table.setColor(row,2, jobFinishedColor)
				table.setItem(row,2,jobs[key]["status"])
				if jobs.has_key("error"):
					table.setItem(row,3,jobs[key]["error"])
				row = row + 1
			
			table.render(self)

