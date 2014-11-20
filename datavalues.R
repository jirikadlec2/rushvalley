#example R-script for plotting values from HydroServer
#this example compares temperature in last month at 5cm and 30cm depth

#to run this script, you must install the XML package
library(XML)


#this function gets the WaterML XML from Hydroserver and converts it
#to a data frame
#this function should be moved to a package
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
  vals <- doc[[2]][[3]]
  
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
  df <- data.frame("time"=as.POSIXct(dt), "DataValue"=val)
  df[df$DataValue == noData,2] <- NA
  df$Date <- as.Date(as.POSIXct(df$time))
  return(df)
}


##############################################
# Change these values to get a different plot#
##############################################
site05 = "Ru1BMP5"
variable = "MPS6_WaterTemp"
startDate = "2014-10-19"
endDate = "2014-11-19"

site30 = "Ru1BMP30"

values5cm = getValues(site05, variable, startDate, endDate)
values30cm = getValues(site30, variable, startDate, endDate)

plot(DataValue~time, data=values5cm, type="l", col="black")
lines(DataValue~time, data=values30cm, type="l", col="red")

legend(x="topright", 
       legend=c(site05, site30), 
       lty=c(1, 1), 
       lwd=c(1, 1), 
       col=c("black", "red"), inset=c(0.01,0.02))


