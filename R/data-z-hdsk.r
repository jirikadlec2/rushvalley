library("waterml")


urlodk = "http://hydrodata.info/webservices/cuahsi_1_1.asmx"

stanice = GetSites(urlodk)
promenne = GetVariables(urlodk)


stan = stanice$FullSiteCode[1]
prom = promenne$FullVariableCode[1]
od = "2010-11-01"
do = "2014-11-21"
co = "max"



hodnoty = GetValues(urlodk,site=stan, variable=prom, startDate=od, endDate=do,daily=co)
