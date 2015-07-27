#This suite of scripts handles both automated and manual data upload to the hydroserver database at worldwater.byu.edu named "rush\_valley". 

*decagon.py handles getting the data from Decagon in dxd files, parsing xls files downloaded directly from dataloggers
*converter.py decodes the data from dxd files into usable values
*data\_transfer.py runs the operarations in decagon.py and converter.py to upload data to rush\_valley
*clean\_logs.py manages the log files saved from automated executions of data\_transfer.py and keeps ony the 14 newest
*passwords.csv has the passwords used by decagon.dxd to get datalogger data from the Decagon API in dxd format
*01\_LookupTable.xlsx is used by data\_transfer.py to look up the relevant info about each logger (logger ID, Site ID, Lat, Lon, Port Number, Sensor ID, Variables)
*dxd/ holds the dxd files from Decagon with datalogger information. These files have all but the most recent data removed each time data\_transfer.py runs, but they are also deleted when run automatically because they are not needed and tend to cause upload problems
*runUpload.sh is used on the worldwater.byu.edu server to run the entire suite of scripts automatically. It is executed by a crontab command every Monday morning at 1AM

To run manually, data\_transfer.py must be executed with the -xls option and a file in .xls format. 5G0E3559-sample.xls is a sample xls file to show correct formatting.
The files will have two tabs; the scripts do not upload the data from the "Unprocessed Data" tab. data\_transfer.py uses functionality from decagon.py to parse the xls files.

