#!/bin/env python
#!/bin/env python

import arc, sys, os

sys.path.append("..")

from Clients import *       

if __name__ == "__main__":
    
    logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient");
    logcout = arc.LogStream(sys.stdout);
    arc.Logger_getRootLogger().addDestination(logcout);
    arc.Logger_getRootLogger().setThreshold(arc.DEBUG);

    userAuth = UserAuthentication()
    userAuth.certificatePath = "/home/jonas/.globus/usercert.pem"
    userAuth.keyPath = "/home/jonas/.globus/userkey.pem"
    userAuth.caDir = "/etc/grid-security/certificates"
    userAuth.createLocalProxy()