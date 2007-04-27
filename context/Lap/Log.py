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

global lapLogger

def _getLapLogger():

	global lapLogger
	logger = None

	try:
		logger = lapLogger
	except:
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
		lapLogger = logger

	return logger


def lapDebug(message):
	"""Log a debug message to LAP log file."""
	logger=_getLapLogger()
	logger.debug(message)
	
def lapInfo(message):
	"""Log an informational message to the LAP log file."""
	logger=_getLapLogger()
	logger.info(message)

def lapWarning(message):
	"""Log a warning message to the LAP log file."""
	logger=_getLapLogger()
	logger.warning(message)

def lapError(message):
	"""Log an error message to the LAP log file."""
	logger=_getLapLogger()
	logger.error(message)
	
def lapCritical(message):
	"""Log a critical message to the LAP log file."""
	logger=_getLapLogger()
	logger.critical(message)
