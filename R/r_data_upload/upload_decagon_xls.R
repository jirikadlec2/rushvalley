#reads the xls file from DECAGON
#uploads the data from the xls file to HydroServer

setwd("C:/jiri/Dropbox/BYU/hydroinformatics/paper/sample_code")

data <- read.table("5G0E3559-processed.txt", sep="\t", header=TRUE, stringsAsFactors=FALSE)
data$time <- strptime(data$Measurement.Time,"%m/%d/%y %I:%M %p", tz="GMT")
names(data)
tail(data)
