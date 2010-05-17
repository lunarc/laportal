#!/usr/bin/env python

import arc
import arcom

userConfig = arc.UserConfig("/home/jonas/.arc/arcgui.conf", "/home/jonas/.arc/jobs.xml")
userConfig.InitializeCredentials()

url = arc.URL("gsiftp://se-ann.lunarc.lu.se/data/jonas")
handle = arc.DataHandle(url, userConfig)
point = handle.__ref__()

(files, status) = point.ListFiles()

for item in files:
    print item.GetName()
    
print status

#files = point.ListFiles()
