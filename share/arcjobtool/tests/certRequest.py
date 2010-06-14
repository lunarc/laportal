import arc

start = arc.Time()
arcPeriod = arc.Period("12", arc.PeriodHours)
              
credRequest = arc.Credential(start, arcPeriod, 1024, "gsi2", "inheritAll", "", -1)
credRequest.AddExtension("subjectAlternativeName", "jonas.lindemann@lunarc.lu.se")
result = credRequest.GenerateEECRequest("usercert.pem", "userkey.pem", "/O=Grid/O=NorduGrid/OU=lunarc.lu.se/CN=Jonas Lindemann")
result, privateKey = credRequest.OutputPrivatekey(encryption=True, passphrase="Hello")

keyFile = open("userkey.pem", "w")
keyFile.write(privateKey)
keyFile.close()
