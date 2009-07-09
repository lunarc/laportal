#!/bin/env python

import os, sys, sha

from optparse import OptionParser

configTemplate = """<?xml version="1.0" encoding="utf-8"?>
<ArcConfig>
  <DefaultServices>
    <URL Flavour="ARC0" ServiceType="index">ldap://index1.swegrid.se:2135/Mds-Vo-name=SweGrid,o=grid</URL>
    <URL Flavour="ARC0" ServiceType="index">ldap://index2.swegrid.se:2135/Mds-Vo-name=SweGrid,o=grid</URL>
  </DefaultServices>
  <CACertificatePath>/etc/grid-security/certificates</CACertificatePath>
</ArcConfig>"""

sys.path.append("/sw/pkg/Webware-1.0.1")

from UserKit.RoleUserManagerToFile import RoleUserManagerToFile

def userExists(userName, userMgr):
       
    for user in userMgr.users():
        if user.name() ==  userName:
            return True

    return False    

if __name__ == "__main__":
    
    # Parse options
    
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", help="username to create.")
    parser.add_option("-o", "--outputdir", dest="outputdir", help="user directory (default=/var/spool/lap)", default="/var/spool/lap")
    parser.add_option("-r", "--reset", dest="reset", default=False, action="store_true", help="reset password")
    (options, args) = parser.parse_args()
           
    if options.reset:
        pass
        sys.exit(0)
        
    # If no username is specified ask for it
        
    userName = ""
        
    if options.username == None:
        userName = raw_input("Please enter username: ")
        if userName == "":
            print "Invalid username given."
            sys.exit(-1)
    else:
        userName = options.username

    userMgr = RoleUserManagerToFile()
    userMgr.setUserDir(options.outputdir)
    userMgr.initNextSerialNum()
    
    # Make username does not exist
           
    if userExists(userName, userMgr):
        print "User already exists. Please choose a different username."
        sys.exit(-1)
        
    # Create user and password
        
    password = raw_input("Please enter user password: ")
    userMgr.createUser(userName, sha.sha(password).hexdigest())
    password = ""
    
    # Create user directory
    
    userDir = os.path.join(options.outputdir, userName) 
    os.mkdir(os.path.join(options.outputdir, userName))
    
    # Create template configuration file
    
    configFilename = os.path.join(userDir,"client.xml")
    configFile = open(configFilename, "w")
    configFile.write(configTemplate)
    configFile.close()    
