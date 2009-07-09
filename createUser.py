#!/bin/env python

import os, sys, sha, getpass

from optparse import OptionParser

configTemplate = """<?xml version="1.0" encoding="utf-8"?>
<ArcConfig>
  <DefaultServices>
    <URL Flavour="ARC0" ServiceType="index">ldap://index1.swegrid.se:2135/Mds-Vo-name=SweGrid,o=grid</URL>
    <URL Flavour="ARC0" ServiceType="index">ldap://index2.swegrid.se:2135/Mds-Vo-name=SweGrid,o=grid</URL>
  </DefaultServices>
  <CACertificatePath>/etc/grid-security/certificates</CACertificatePath>
</ArcConfig>"""

def userExists(userName, sessionDir="/var/spool/lap"):
    """
    Check if a username already is created.
    """
    
    userDir = os.path.join(sessionDir, userName)
    
    if os.path.exists(userDir):
        return True
    else:
        return False
    
def createUser(userName, passwordHash, sessionDir="/var/spool/lap"):
    """
    Create user directory and configuration files.
    """
    
    # Create user directory
    
    userDir = os.path.join(sessionDir, userName) 
    os.mkdir(userDir)
    
    # Create user.passwd file
    
    userPasswdFilename = os.path.join(userDir,"user.passwd")
    
    userPasswdFile = open(userPasswdFilename, "w")
    userPasswdFile.write(passwordHash)
    userPasswdFile.close()
    
    os.chmod(userPasswdFilename, 0600)
    
    # Create template configuration file
    
    configFilename = os.path.join(userDir,"client.xml")
    configFile = open(configFilename, "w")
    configFile.write(configTemplate)
    configFile.close()    
    

if __name__ == "__main__":
    
    # Parse options
    
    parser = OptionParser()
    parser.add_option("-u", "--username", dest="username", help="username to create.")
    parser.add_option("-o", "--outputdir", dest="outputdir", help="user directory (default=/var/spool/lap)", default="/var/spool/lap")
    parser.add_option("-r", "--reset", dest="reset", default=False, action="store_true", help="reset password")
    (options, args) = parser.parse_args()
           
    if options.reset:
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
        
    # Ask for password
    
    password = getpass.getpass("Enter password:  ")
    
    if password == "":
        print "Invalid password given."
        sys.exit(-1)

    # Make username does not exist
           
    if userExists(userName, options.outputdir):
        print "User already exists. Please choose a different username."
        sys.exit(-1)
        
    # Create user and password
    
    createUser(userName, sha.sha(password).hexdigest(), options.outputdir)
    password = "                        "
        
