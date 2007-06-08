#
# Logging module
#
# Copyright (C) 2006-2007 Jonas Lindemann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""Logging module"""

import logging
import LapSite

from threading import Lock

global lapLogger

class LapLogger:
    """ LAP Logger """

    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if LapLogger.__instance is None:
            # Create and remember instance
			
			logger = logging.getLogger('lap')
			hdlr = logging.FileHandler(LapSite.Logging["LogFile"])
			formatter = logging.Formatter('%(asctime)s %(levelname)s\t: %(message)s')
			hdlr.setFormatter(formatter)
			logger.addHandler(hdlr)
	
			if LapSite.Logging.has_key("LogLevel"):
					if LapSite.Logging["LogLevel"] == "DEBUG":
							logger.setLevel(logging.DEBUG)
					elif LapSite.Logging["LogLevel"] == "WARNING":
							logger.setLevel(logging.WARNING)
					elif LapSite.Logging["LogLevel"] == "INFO":
							logger.setLevel(logging.INFO)
					else:
							logger.setLevel(logging.WARNING)
			else:
					logger.setLevel(logging.WARNING)
	
			logger.info("Logging started.")
			logger.warning("Logging started.")
			logger.error("Logging stated.")
			
			LapLogger.__instance = logger

        # Store instance reference as the only member in the handle
        self.__dict__['_LapLogger__instance'] = LapLogger.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)


def lapDebug(message):
	"""Log a debug message to LAP log file."""
	logger=LapLogger()
	logger.debug(message)
	
def lapInfo(message):
	"""Log an informational message to the LAP log file."""
	logger=LapLogger()
	logger.info(message)

def lapWarning(message):
	"""Log a warning message to the LAP log file."""
	logger=LapLogger()
	logger.warning(message)

def lapError(message):
	"""Log an error message to the LAP log file."""
	logger=LapLogger()
	logger.error(message)
	
def lapCritical(message):
	"""Log a critical message to the LAP log file."""
	logger=LapLogger()
	logger.critical(message)
