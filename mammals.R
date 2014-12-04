#example R-script for plotting values from HydroServer
#this example compares temperature in last month at 5cm and 30cm depth

#to run this script, you must install the XML package
library(XML)
library(RCurl)

#this function gets the Sites from Hydroserver.
#it converts the sites to a data.frame object
getSites <- function(url) {
  sites_url <- paste(url, "/GetSitesObject", sep="")
  text <- getURL(sites_url)
  doc <- xmlRoot(xmlTreeParse(text, getDTD=FALSE, useInternalNodes = TRUE))
  N <- xmlSize(doc) - 1 #because first element is queryInfo
  
   df <- data.frame(SiteName=rep("",N), SiteCode=rep("",N), Latitude=rep(NA,N), 
                    Longitude=rep(NA,N), Elevation=rep(NA,N),State=rep("",N),
                    County=rep("",N), Comments=rep("",N), stringsAsFactors=FALSE)
  
  for(i in 1:N){
  
    siteInfo <- doc[[i+1]][[1]]
    siteList <- xmlToList(siteInfo)
    siteName <- siteList$siteName
    siteCode <- siteList$siteCode$text
    latitude <- as.numeric(siteList$geoLocation$geogLocation$latitude)
    longitude <- as.numeric(siteList$geoLocation$geogLocation$longitude)
    elevation <- as.numeric(siteList$elevation_m)
    comments <- NA
    state <- NA
    county <- NA
  
    numElements <- xmlSize(siteInfo)
    for (j in 1: numElements){
      element <- siteInfo[[j]]
      
      if (is.null(element)) {
        print ('element is null!')
        next
      }
      if (xmlName(element) != 'siteProperty') next
      
      attr <- xmlAttrs(element)["name"]
      if (attr == 'SiteComments') {
        comments <- xmlValue(element)
      }
      if (attr == 'State') {
        state <- xmlValue(element)
      }
      if (attr == 'County') {
        county <- xmlValue(element)
      }     
    }
    df$SiteName[i] <- siteName
    df$SiteCode[i] <- siteCode
    df$Latitude[i] <- latitude
    df$Longitude[i] <- longitude
    df$Elevation[i] <- elevation
    df$Comments[i] <- comments
    df$State[i] <- state
    df$County[i] <- county
 } 
}


#this function gets the WaterML XML from Hydroserver and converts it
#to a data frame
#this function should be moved to a package
#TODO: add error checking
getValues <- function(site, variable, startDate, endDate) {
  base_url = "http://worldwater.byu.edu/interactive/rushvalley/services/index.php/cuahsi_1_1.asmx/GetValuesObject"
  network = "WWO" 
  url = paste(base_url, "?location=", network, ":", site, 
              "&variable=", network, ":", variable, sep="",
              "&startDate=",startDate, "&endDate=",endDate)
  
    text = getURL(url)
    doc = xmlRoot(xmlTreeParse(text, getDTD=FALSE, useInternalNodes = TRUE))
  
    variable <- xmlToList(doc[[2]][[2]])
    noData <- as.numeric(variable$noDataValue)
  
  
    vals <- doc[[2]]
    
    if (is.null(vals)){
      print(paste("no data values found:", url))
      return(NULL)
    }
  
    valCount = xmlSize(vals)
    xmNames = xmlSApply(vals, xmlName)
    val = c()
    dt = c()
    for (j in 1:valCount){
      if(xmlName(vals[[j]]) == 'value') {
        dt[j] <- xmlAttrs(vals[[j]])["dateTime"]
        val[j] <- as.numeric(xmlValue(vals[[j]]))
      }
    }
  
    if (is.null(val) | is.null(dt)){
      return (NULL)
    }
  
    df <- data.frame("time"=as.POSIXct(dt), "DataValue"=val)
    df[df$DataValue == noData,2] <- NA
    df$Date <- as.Date(as.POSIXct(df$time))
  
  return(df)
}


##############################################
# Change these values to get a different plot#
##############################################

no_mammal = c("Ru1BMP5", "Ru2BNMA", 
"Ru4BNCA", "Ru4BNMA", "Ru5BNM5", "Ru5BNN5", "RU4BNCA", "Ru4BNNU", "Ru4BNPA", "Ru4BNMA",
"Ru5BNPA", "Ru5BNNA", "Ru5BNPA", "Ru1BNCA", "Ru1BNNU", "Bu2BNPA", "Ru2BNCA")

mammal = c("Ru1BMPA", "Ru1BMNA", "Ru5BMCA", "Ru1BMNU", "Ru5BMMA", "Ru2BMPA", "Ru2BMN5", "Ru3BMMA",
           "Ru3BMPA", "Ru4BMPA", "Ru4BMNA", "Ru2BMMA", "Ru2BMNU", "Ru3BMNA", "Ru3BMNU", "Ru4BMMA",
           "Ru5BMPA", "Ru1BMMA")

#get data for mammal
startDate = "2014-08-01"
endDate = "2014-10-15"
variable = "SRS_Nr_NDVI"
site = no_mammal[1]
data1 = getValues(site, variable, startDate, endDate)
#get the daily average
#get the daily maximum
validdata <- na.omit(data1)

dailyMean = aggregate(validdata$DataValue, list(validdata$Date), mean)
dailyMax = aggregate(validdata$DataValue, list(validdata$Date), max)
plot(dailyMax, type="l")


for (i in 2:length(no_mammal)) {
  
    site = no_mammal[i]
    data = getValues(site, variable, startDate, endDate)
    
    if (length(data) > 1) { next }
    
    data1 <- rbind(data1, data) 
    nrow(data)
}
data1$mammal = "No Mammals"

site = mammal[1]
data2 = getValues(site, variable, startDate, endDate)

for (i in 2:length(mammal)) {
  
  site = mammal[i]
  data = getValues(site, variable, startDate, endDate)
  
  if (length(data) > 1) { next }
  
  data2 <- rbind(data2, data)  
}
data2$mammal = "Mammals"

dataALL <- rbind(data2, data1)
boxplot(DataValue~mammal, data=dataALL)
heading <- paste("temperature:", startDate, "-", endDate, sep=" ")
title (main=heading, xlab="treatment", ylab="temperature (°C)")




