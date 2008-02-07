
Application = {
	"ContextName":"context"
}

Logging = {
	"LogFile":"/var/log/lap/lap.log",
	"WebWareLogFile":"/var/log/lap/lap_ww.log",
        "LogLevel":"DEBUG"
}

Dirs = {
    "PluginDir":"/sw/lap/context/Plugins",
    "SessionDir":"/var/spool/lap",
    "WebWareDir":"/sw/Webware-0.9.3",
    "AppWorkDir":"/sw/lap",
    "DependsDir":"/sw/lap/depends",
    "NorduGridDir":"/opt/nordugrid"
}

Appearance = {
	"WelcomeMessage":"Welcome to the LUNARC application portal",
	"WebSiteName":"LUNARC",
	"LogoImage":"images/logo.png",
	"LogoImageWidth":"445px",
	"LogoImageHeight":"86px"
}

Admin = {
	"VOAdmin":"/O=Grid/O=NorduGrid/OU=byggmek.lth.se/CN=Jonas Lindemann",
	"VOSites":["130.235.7.91"],
	"UserAdmin":"/O=Grid/O=NorduGrid/OU=byggmek.lth.se/CN=Jonas Lindemann",
	"UserSites":["130.235.7.91"],
	"UserListEnabled":False
}

System = {
        "SMTPServer":"mail.lth.se",
	"ServerUser":"portaluser",
	"ServerGroup":"lunarc",
	"ServerPIDFile":"/var/run/lap.pid",
	"ARCInterface":""
}
