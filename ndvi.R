#example R-script for plotting values from HydroServer
#this example compares ndvi for 'mammal' and 'no mammal'

#to run this script, you must install the packages XML, RCurl, plyr, ggplot2
require(XML)
require(RCurl)
require(plyr)
require(ggplot2)

#####################################################
# FUNCTION: getVariables                            #
#this function gets the Variables from Hydroserver. #
#it converts the sites to a data.frame object       #
# TODO: Move getSites to WaterML package !          #
#####################################################
getVariables <- function(server) {
  variables.url <- paste(server, "/GetVariablesObject", sep="")
  text <- getURL(variables.url)
  doc <- xmlRoot(xmlTreeParse(text, getDTD=FALSE, useInternalNodes = TRUE))  
  vars <- doc[[2]]
  N <- xmlSize(vars)
  #define the columns
  df <- data.frame(VariableCode=rep("",N), VariableName=rep("",N), ValueType=rep("",N), 
                   DataType=rep("",N), GeneralCategory=rep("",N),SampleMedium=rep("",N),
                   UnitName=rep("",N), UnitType=rep("",N), UnitAbbreviation=rep("",N), 
                   NoDataValue=rep(NA,N), IsRegular=rep("",N), 
                   TimeUnitName=rep("",N), TimeUnitAbbreviation=rep("",N),
                   TimeSupport=rep("",N), Speciation=rep("",N), stringsAsFactors=FALSE)
  for(i in 1:N) {
    varObj <- vars[[i]]
    v <- xmlToList(varObj)
    df$VariableCode[i] <- v$variableCode$text
    df$VariableName[i] <- v$variableName
    df$ValueType[i] <- v$valueType
    df$DataType[i] <- v$dataType
    df$GeneralCategory[i] <- v$generalCategory
    df$SampleMedium[i] <- v$sampleMedium
    df$UnitName[i] <- v$unit$unitName
    df$UnitType[i] <- v$unit$unitType
    df$UnitAbbreviation[i] <- v$unit$unitAbbreviation
    df$NoDataValue <- as.numeric(v$noDataValue)
    df$IsRegular <- v$timeScale$.attrs["isRegular"]
    df$TimeUnitName <- v$timeScale$unit$unitName
    df$TimeUnitAbbreviation <- v$timeScale$unit$unitAbbreviation
    df$TimeSupport <- v$timeScale$timeSupport
    df$Speciation <- v$speciation
  }
  return(df)
}



#################################################
# FUNCTION: getSites                            #
#this function gets the Sites from Hydroserver. #
#it converts the sites to a data.frame object   #
# TODO: Move getSites to WaterML package !      #
#################################################
getSites <- function(server) {
  sites_url <- paste(server, "/GetSitesObject", sep="")
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
 return(df)
}


##################################################
# FUNCTION: getValues                            #
#this function gets the values from Hydroserver. #
#it converts the sites to a data.frame object    #
#parameters:                                     #
# server:   the hydroserver web services URL     #
# site:     the site code                        #
# variable: the variable code                    #
# startDate: the start date and time 'yyyy-mm-dd'#
# endDate:   the end date and time 'yyyy-mm-dd'  #
# daily (optional): use 'max' or 'mean' to get   #
#                   daily aggregated values      #
# TODO: Add better error checking                #
# TODO: Move getValues to WaterML package        #
##################################################
getValues <- function(server, site, variable, startDate, endDate, daily=NULL) {
  base_url <- paste(server, "/GetValuesObject", sep="")
  network = "WWO" 
  url = paste(base_url, "?location=", network, ":", site, 
              "&variable=", network, ":", variable, sep="",
              "&startDate=",startDate, "&endDate=",endDate)
  print(url)
  
    text = getURL(url)
    doc = xmlRoot(xmlTreeParse(text, getDTD=FALSE, useInternalNodes = TRUE))
  
    variable <- xmlToList(doc[[2]][[2]])
    noData <- as.numeric(variable$noDataValue)
  
  
    vals <- doc[[2]][[3]]
    
    if (is.null(vals)){
      print(paste("no data values found:", url))
      return(NULL)
    }
    if (xmlValue(vals) == "") {
      print(paste("no data values found:", url))
      return(NULL)
    }
  
    valCount = xmlSize(vals)
    print(paste("valCount:", valCount))
    xmNames = xmlSApply(vals, xmlName)
    val = c()
    dt = c()
    for (j in 1:valCount){
      if(xmlName(vals[[j]]) == 'value') {
        dt <- c(dt, xmlAttrs(vals[[j]])["dateTime"])
        val <- c(val, as.numeric(xmlValue(vals[[j]])))
      }
    }
  
    print(length(val))
    if (length(val) == 0) {
      return (NULL)
    }
    
   
    df <- data.frame("time"=as.POSIXct(dt), "DataValue"=val)
    df[df$DataValue == noData,2] <- NA
  
    if (!is.null(daily)) {
      validdata <- na.omit(df)
      if (nrow(validdata) == 0) {
        print("no valid data found!")
        return (NULL)
      }
      validdata$time <- as.Date(as.POSIXct(validdata$time))
      if (daily=="max") {
        dailyMax = aggregate(validdata$DataValue, list(validdata$time), max)
        names(dailyMax)[1] <- "time"
        names(dailyMax)[2] <- "DataValue"
        return(dailyMax)
      } else if (daily=="mean") {
        dailyMean = aggregate(validdata$DataValue, list(validdata$time), mean)
        names(dailyMean)[1] <- "time"
        names(dailyMax)[2] <- "DataValue"
        return(dailyMean)
      }
    }
  
  return(df)
}



###############################################
# Example: Query the sites by treatment       #
###############################################

server <- "http://worldwater.byu.edu/interactive/rushvalley/services/index.php/cuahsi_1_1.asmx"
all_sites <- getSites(server)

#add column for mammal treatment: 5th letter in the code
all_sites$Mammals <- substring(all_sites$SiteCode, 5, 5)

#sites with 'no mammal' treatment
sites_no_mammal <- all_sites[all_sites$Mammals=="N",]
#sites with 'mammal' treatment
sites_mammal <- all_sites[all_sites$Mammals=="M",]

#########################################################################
# Example: Get daily max NDVI's by mammal treatment in the long format  #
# change startDate, endDate, variable to show different plot !!         #
#########################################################################
startDate = "2014-10-07"
endDate = "2014-10-15"
variable = "SRS_Nr_NDVI"

data <- NULL
col.index <- 0

for (i in 1: nrow(all_sites)) {
  sitecode <- all_sites$SiteCode[i]
  new_data <- getValues(server, sitecode, variable, startDate, endDate, daily="max")
  
  #skip sites with no NDVI data in this time period
  if (is.null(new_data)) {
    print ('no data!')
    next
  }
  print(sitecode)
  new_data$site <- sitecode
  new_data$treatment <- substring(sitecode, 5, 5) #to indentify mammal/no mammal
  #add the site's data to the data frame
  data <- rbind(data, new_data)
}

##################################################################################
# Example: Plot the error bar plot, mammals vs. no mammals                       #
# see: http://www.cookbook-r.com/Graphs/Plotting_means_and_error_bars_(ggplot2)/ #
##################################################################################
require(ggplot2)
require(plyr)
#we summarize the data by day and treatment
data.summarized <- ddply(data, ~time+treatment, summarise, mean=mean(DataValue), sd=sd(DataValue))
#rename the variable
names(data.summarized)[3] <- "daily.max.NDVI"
# Daily plot: no error bars
ggplot(data.summarized, aes(x=time, y=daily.max.NDVI, colour=treatment)) + 
  geom_line() +
  geom_point()

# Daily plot: errorbars
# The errorbars overlapped, so use position_dodge to move them horizontally
pd <- position_dodge(0.25) # move them .05 to the left and right

ggplot(data.summarized, aes(x=time, y=daily.max.NDVI, ymax=max(daily.max.NDVI), colour=treatment)) + 
  geom_errorbar(aes(ymin=daily.max.NDVI-sd, ymax=daily.max.NDVI+sd), width=.5, position=pd) +
  geom_line(position=pd) +
  geom_point(position=pd)
