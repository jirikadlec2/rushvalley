#########################################################################
#before running this script first time, you must install the packages:  #
# WaterML, reshape2, ggplot2                                            #
#########################################################################
install.packages(c("WaterML", "reshape2", "ggplot2"))
library(WaterML)
library(reshape2)
library(ggplot2)

#################################################################
# STEP (1) select sites that measure NDVI site code ends with A)#
#################################################################
server <- "http://worldwater.byu.edu/app/index.php/rushvalley/services/cuahsi_1_1.asmx?WSDL"
sites <- GetSites(server)
NDVI_sites <- sites[grepl(sites$SiteCode, pattern=".A$"),]
View(NDVI_sites)

#################################################################
# STEP (2) get details about the ndvi measuring sites           # 
# including variable, first and last available measurement date #
#################################################################
ndvi_site_infos <- data.frame()
for(sc in NDVI_sites$FullSiteCode) {
  si <- GetSiteInfo(server, sc)
  ndvi_site_infos <- rbind(ndvi_site_infos, si)
}

#################################################################
# STEP (3) download all the values with the NDVI data           #
#################################################################

##################################################
# NOTE: you can set start_date and end_date here.#
##################################################
start_date <- "2014-06-01"
end_date <- "2015-06-30"

ndvi_values <- data.frame()
for (i in 1: nrow(ndvi_site_infos)) {
  fullSiteCode <- ndvi_site_infos$FullSiteCode[i]
  fullVariableCode <- ndvi_site_infos$FullVariableCode[i]
  siteCode <- ndvi_site_infos$SiteCode[i]
  variableCode <- ndvi_site_infos$VariableCode[i]
  v <- GetValues(server, siteCode, variableCode, start_date, end_date)
  # add siteCode, variableCode to the data
  v$SiteCode <- siteCode
  v$VariableCode <- variableCode
  ndvi_values <- rbind(ndvi_values, v)
}

#separate data by variable
ndvi_630 <- subset(ndvi_values, VariableCode=="SRS_Nr_NDVI_sixthirty")
ndvi_800 <- subset(ndvi_values, VariableCode=="SRS_Nr_NDVI_eighthundred")
ndvi_index <- subset(ndvi_values, VariableCode=="SRS_Nr_NDVI")

#########################################################################
# STEP (4) Save 3 .CSV files: ndvi_630, ndvi_800, ndvi_index            #
#########################################################################
library(reshape2)
ndvi_630_wide <- dcast(ndvi_630, time~SiteCode, value.var="DataValue")
ndvi_800_wide <- dcast(ndvi_800, time~SiteCode, value.var="DataValue")
ndvi_index_wide <- dcast(ndvi_index, time~SiteCode, value.var="DataValue")
write.csv(ndvi_630_wide, "ndvi_630.csv")
write.csv(ndvi_800_wide, "ndvi_800.csv")
write.csv(ndvi_index_wide, "ndvi_index.csv")

##########################################################################
# example how to plot all the data using ggplot2. This example is for 630#                         #
##########################################################################
library(ggplot2)
ggplot(data=ndvi_630,
       aes(x=time, y=DataValue, colour=SiteCode, group=SiteCode)) +
       geom_line()
