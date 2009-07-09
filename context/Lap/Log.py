#
# Logging module
#
# Copyright (C) 2006-2008 Jonas Lindemann
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

import os

import logging
import LapSite

class LogSingleton:
	"""A python singleton http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52558"""
	
	class __impl:
		""" Implementation of the singleton interface """
		
		def __init__(self):
			print "LogSingleton"
			print "    current uid = ", os.getuid()
			self.__logger = logging.getLogger('lap')
			
			if LapSite.Logging.has_key("LogLevel"):
				if LapSite.Logging["LogLevel"] == "DEBUG":
					self.__logger.setLevel(logging.DEBUG)
				elif LapSite.Logging["LogLevel"] == "WARNING":
					self.__logger.setLevel(logging.WARNING)
				elif LapSite.Logging["LogLevel"] == "INFO":
					self.__logger.setLevel(logging.INFO)
				else:
					self.__logger.setLevel(logging.WARNING)
			else:
				self.__logger.setLevel(logging.WARNING)
	
		def getLogger(self):
			return self.__logger
		
		def setup(self):
			hdlr = logging.FileHandler(LapSite.Logging["LogFile"])
			formatter = logging.Formatter('%(asctime)s %(levelname)s\t: %(message)s')
			hdlr.setFormatter(formatter)
			self.__logger.addHandler(hdlr)
			

	# storage for the instance reference
	__instance = None

	def __init__(self):
		""" Create singleton instance """
		# Check whether we already have an instance
		if LogSingleton.__instance is None:
			# Create and remember instance
			LogSingleton.__instance = LogSingleton.__impl()
	
		# Store instance reference as the only member in the handle
		self.__dict__['_LogSingleton__instance'] = LogSingleton.__instance
	
	def __getattr__(self, attr):
		""" Delegate access to implementation """
		return getattr(self.__instance, attr)
	
	def __setattr__(self, attr, value):
		""" Delegate access to implementation """
		return setattr(self.__instance, attr, value)

def lapDebug(message):
	"""Log a debug message to LAP log file."""
	logSingleton=LogSingleton()
	logSingleton.getLogger().debug(message)
	
def lapInfo(message):
	"""Log an informational message to the LAP log file."""
	logSingleton=LogSingleton()
	logSingleton.getLogger().info(message)

def lapWarning(message):
	"""Log a warning message to the LAP log file."""
	logSingleton=LogSingleton()
	logSingleton.getLogger().warning(message)

def lapError(message):
	"""Log an error message to the LAP log file."""
	logSingleton=LogSingleton()
	logSingleton.getLogger().error(message)
	
def lapCritical(message):
	"""Log a critical message to the LAP log file."""
	logSingleton=LogSingleton()
	logSingleton.getLogger().critical(message)
	
def lapSetupLogging():
	logSingleton=LogSingleton()
	logSingleton.setup()
	
