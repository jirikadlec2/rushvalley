#example R-script for plotting values from HydroServer
#this example compares ndvi for 'mammal' and 'no mammal'

#to run this script, you must install the packages devtools, XML, RCurl, plyr, ggplot2
require(XML)
require(RCurl)
require(plyr)
require(ggplot2)

#install the development version of the waterml package!
library(waterml)

#########################################################################
# Example: Get daily max NDVI's by mammal treatment in the long format  #
# change startDate, endDate, variable to show different plot !!         #
#########################################################################
server <- "http://worldwater.byu.edu/app/index.php/rushvalley/services/cuahsi_1_1.asmx"
startDate = "2014-10-07"
endDate = "2014-10-15"
variable = "SRS_Nr_NDVI"

#get the sites
all_sites <- GetSites(server)

#get the variables
all_variables <- GetVariables(server)

#get the values from all sites that measure NDVI
data <- NULL
col.index <- 0
#we use a loop to get all the time series and put them together
for (i in 1: nrow(all_sites)) {
  sitecode <- all_sites$SiteCode[i]
  new_data <- GetValues(server, sitecode, variable, startDate, endDate, daily="max")

  #skip sites that don't have NDVI data in this time period
  if (is.null(new_data)) {
    print ('no data!')
    next
  }
  #print(sitecode)
  #we add the site and treatment column to identify the site and the treatment
  new_data$site <- sitecode
  #to indentify mammal/no mammal treatment we use the 5th character or the SiteCode
  new_data$treatment <- substring(sitecode, 5, 5)
  #we add the site's data to the data frame
  data <- rbind(data, new_data)
}

##################################################################################
# Example: Plot the error bar plot, mammals vs. no mammals                       #
# see: http://www.cookbook-r.com/Graphs/Plotting_means_and_error_bars_(ggplot2)/ #
##################################################################################

#we summarize the data by day and treatment
data.summarized <- ddply(data, ~time+treatment, summarise, mean=mean(DataValue), sd=sd(DataValue))
#rename the variable to better name
names(data.summarized)[3] <- "daily.max.NDVI"
# Daily plot: no error bars
ggplot(data.summarized, aes(x=time, y=daily.max.NDVI, colour=treatment)) +
  geom_line() +
  geom_point()

# Daily plot: errorbars
# The errorbars overlapped, so we use position_dodge to move them horizontally
pd <- position_dodge(0.25) # move them .05 to the left and right

ggplot(data.summarized, aes(x=time, y=daily.max.NDVI, ymax=max(daily.max.NDVI), colour=treatment)) +
  geom_errorbar(aes(ymin=daily.max.NDVI-sd, ymax=daily.max.NDVI+sd), width=.5, position=pd) +
  geom_line(position=pd) +
  geom_point(position=pd)
