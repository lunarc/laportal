#!/bin/env python

import arc, sys, os;

sys.path.append("../../../lib")

from arcjobtool.ArcUtils import *

print "--- Setup logging ---"

logger = arc.Logger(arc.Logger_getRootLogger(), "ArcClient");
logcout = arc.LogStream(sys.stdout);
arc.Logger_getRootLogger().addDestination(logcout);
arc.Logger_getRootLogger().setThreshold(arc.ERROR);

print "--- Load user configuration ---"

userConfig = arc.UserConfig("/home/jonas/.arc/arcjobtool.conf", "/home/jonas/.arc/jobs.xml")
userConfig.InitializeCredentials()
userConfig.LoadConfigurationFile("home/jonas/.arc/arcjobtool.conf")

serviceList = ["ARC0:ldap://index3.swegrid.se:2135/Mds-Vo-name=SweGrid,o=grid"]

userConfig.AddServices(serviceList, arc.INDEX)

selectedServices = userConfig.GetSelectedServices(arc.INDEX)

for service in selectedServices["ARC0"]:
    print service.fullstr()


