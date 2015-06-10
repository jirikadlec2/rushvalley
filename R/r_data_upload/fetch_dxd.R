library(httr)

# This functions downloads he dxd file
# by default the mrid is set to zero
download_dxd_file <- function(deviceid, devicepass, mrid=0) {
  # settings for downloading decagon DXD file
  email = 'no-email@byu.edu'
  userpass = 'M-wuJf5!fu5554v'
  url = 'http://api.ech2odata.com/dfmp/dxd.cgi'
  report = 1
  
  body = list(email=email, userpass=userpass, report=report, deviceid=deviceid, 
              devicepass=devicepass, mrid=mrid)
  response <- POST(url=url, body=body, encode="form")
  
  #if response is HTTP 200 OK:
  content(response, "text")
  bin <- content(response, "raw")
  writeBin(bin, paste(deviceid, "dxd", sep="."))
}

#downloads all the data from decagon devices
#password_file contains the decagon device IDs and device passwords.
#password_file is a .csv file
download_all_decagon <- function(password_file) {
  devices <- read.csv(password_file, header=TRUE, stringsAsFactors=FALSE)
  for (i in 1:nrow(devices)){
    deviceid = devices$DeviceID[i]
    devicepassword = devices$password[i]
    print(deviceid)
    download_dxd_file(deviceid, devicepassword)
  }
}

setwd("C:/jiri/dropbox/BYU/hydroinformatics/paper/sample_code")
password_file = "passwords.csv"
download_all_decagon(password_file)
