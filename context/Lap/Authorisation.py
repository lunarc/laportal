#
# Authorisation module
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

"""Authorisation module"""

import LapSite
import os

def isUserAuthorised(userDN):
    """Returns True if DN is authorised
    
    Loads a file, userlist.txt, located in LapSite.Dirs["SessionDir"] and
    queries this file for authorised users. LapSite.Admin["UserListEnabled"]
    must be set to True to use this file. If set to False all users are
    authorised by default."""
    
    UserListEnabled = LapSite.Admin["UserListEnabled"]
    
    if not UserListEnabled:
        return True
    
    if userDN == LapSite.Admin["UserAdmin"]:
        return True
    
    sessionDir = LapSite.Dirs["SessionDir"]
    userListFilename = os.path.join(sessionDir, "userlist.txt")
    
    userList = []
    userDict = {}
    
    lines = []

    if os.path.exists(userListFilename):
            userListFile = file(userListFilename)
            lines = userListFile.readlines()
            userListFile.close()
    
    for line in lines:
            userListDN = line.strip()
            if userListDN == userDN:
                return True
            
    return False
