#
# Dialog module
#
# Copyright (C) 2006 Jonas Lindemann
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

"""Dialog module

Contains some default functions for rendering standard messageboxes. All
functions take the page class as the first argument."""

import os
import sys

from HyperText.HTML import *

import Utils
import Templates

from WebKit.Page import Page

LapHeaderTextColor = "255,255,255"
LapHeaderColor = "123, 154, 192"
LapTextColor = "0,0,0"
LapDefaultColor = "218, 227, 237"

def pleaseWaitBox(page, message):
	"""Render a please wait message."""

	params = {
		"message":message
	}

	page.write(Templates.pleaseWaitTemplate % params)	

def messageBox(page, message, title="Message", gotoPage="", caption="OK", width="20em"):
	"""Render a standard message box
	
	The gotoPage parameter determines what page to redirect to when the user
	presses the OK button."""
	
	if width=="":
		window = DIV(klass="lapWindow")
	else:
		window = DIV(klass="lapWindow", style="width: %s;" % width)
		
	windowHead = DIV(H2(title),klass="lapWindowHead")
	window.append(windowHead)
	windowBody = DIV(klass="lapWindowBody")
	window.append(windowBody)
	
	windowBody.append(BR(),CENTER(message, style="font-size: 80%;"),BR())
	
	form = FORM(INPUT(type="submit", value=caption), method="Post", action=gotoPage)
	windowBody.append(CENTER(form))
	
	page.writeln(BR(),BR(),window)

def infoBox(page, message, title="Message", width="20em"):
	"""Render a informational window."""
	
	if width=="":
		window = DIV(klass="lapWindow")
	else:
		window = DIV(klass="lapWindow", style="width: %s;" % width)
		
	windowHead = DIV(H2(title),klass="lapWindowHead")
	window.append(windowHead)
	windowBody = DIV(klass="lapWindowBody")
	window.append(windowBody)
	
	windowBody.append(BR(),CENTER(message, style="font-size: 80%;"),BR())
	
	page.writeln(window)

def messageBoxYesNo(page, message, title="Question", yesMethod = "", noMethod="", width="20em"):
	"""Render a yes/no messagebox
	
	The yesMethod and noMethod determines the action to take when pressing
	yes or no."""
	
	if width=="":
		window = DIV(klass="lapWindow")
	else:
		window = DIV(klass="lapWindow", style="width: %s;" % width)
		
	windowHead = DIV(H2(title),klass="lapWindowHead")
	window.append(windowHead)
	windowBody = DIV(klass="lapWindowBody")
	window.append(windowBody)
	
	windowBody.append(BR(),CENTER(message, style="font-size: 80%;"),BR())

	form = FORM(
		INPUT(type="submit", value="Yes", name=yesMethod),
		INPUT(type="submit", value="No", name=noMethod),
		method="Post"
	)
	
	windowBody.append(CENTER(form))
	
	page.writeln(BR(),BR(),window)	


