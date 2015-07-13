#select sites that measure NDVI (code ends with A)
server <- "http://worldwater.byu.edu/app/index.php/rushvalley/services/cuahsi_1_1.asmx?WSDL"
sites <- GetSites(server)
NDVI_sites <- sites[grepl(sites$SiteCode, pattern=".A$"),]
View(NDVI_sites)

#select the details about these sites
site_infos <- data.frame()
for(sc in NDVI_sites$FullSiteCode) {
  si <- GetSiteInfo(server, sc)
  site_infos <- rbind(site_infos, si)
}

#select the site infos about all sites
all_site_details <- data.frame()
for(sc in sites$FullSiteCode) {
  si <- GetSiteInfo(server, sc)
  site_infos <- rbind(site_infos, si)
}
write.csv(site_infos, "latest_data_values.csv")
