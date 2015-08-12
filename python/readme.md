#Automated And Manual Data Upload

This suite of scripts handles both automated and manual data upload to the hydroserver database at worldwater.byu.edu named "rush\_valley". 

1. decagon.py handles getting the data from Decagon in dxd files, or parsing xls files downloaded directly from dataloggers if uploading manually
2. converter.py decodes the data from dxd files into usable values
3. data\_transfer.py runs the operarations in decagon.py and converter.py to upload data to rush\_valley
4. clean\_logs.py manages the log files saved from automated executions of data\_transfer.py and keeps only the 14 newest
5. passwords.csv has the passwords used by decagon.dxd to get datalogger data from the Decagon API in dxd format
6. 01\_LookupTable.xlsx is used by data\_transfer.py to look up the relevant info about each logger (logger ID, Site ID, Lat, Long, Port Number, Sensor ID, Variables)
7. dxd/ holds the dxd files from Decagon with datalogger information. These files have all but the most recent data removed each time data\_transfer.py runs, 
but they are also deleted when run automatically because they are not needed and tend to cause upload problems
8. runUpload.sh is used on the worldwater.byu.edu server to run the entire suite of scripts automatically. It is executed by a crontab command every Monday morning at 1AM
9. name\_fixer.py can be used to strip whitespace from filenames, as dataloggers automatically put whitespace in
10. manual\_
