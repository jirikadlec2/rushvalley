#example R-script for plotting box plot of temperature for mammal and no mammal

#to run this script, you must install the XML and RCurl packages
#you must also install the waterml package with
# Tools - install packages - install from package archive file (.zip, .tar.gz)
library(XML)
library(RCurl)
library(waterml)

variable = "MPS6_WaterTemp"
startDate = "2014-09-01"
endDate = "2014-09-10"

server = "http://worldwater.byu.edu/interactive/rushvalley/services/index.php/cuahsi_1_1.asmx"
sites = GetSites(server)

#only use sites with 5cm depth - depth is after 7th character in SiteCode
sites$depth = substring(sites$SiteCode, 7)
sites5cm = sites[sites$depth == 5,]

values <- NULL
col.index <- 0
#we use a loop to get all the time series from every sensor in 5cm depth
#and put them together
for (i in 1: nrow(sites5cm)) {
  sitecode = sites5cm$SiteCode[i]
  new_values = GetValues(server, sitecode, variable, startDate, endDate)

  #if the sensor has data, put it together with data from other sensors
  if (!is.null(new_values)) {
    new_values$site = sitecode
    new_values$treatment = substring(sitecode, 5, 5)
    values = rbind(values, new_values)
    next
  }
}

boxplot(DataValue~treatment, data=values)
heading <- paste(variable, ":", startDate, "-", endDate, sep=" ")
title (main=heading, xlab="treatment", ylab=variable)
