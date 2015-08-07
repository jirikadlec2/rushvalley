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

To run manually, data\_transfer.py must be executed with the -xls option and a file in .xls format. 5G0E3559-sample.xls is a sample xls file to show correct formatting.
The files will have two tabs; the scripts do not upload the data from the "Unprocessed Data" tab. data\_transfer.py uses functionality from decagon.py to parse the xls files.

###Important For Manual Upload###
Before running manual upload, query most recent upload date for the datalogger. The datalogger name is in each filename from the loggers. For example, if the filename is "5G0E3559 27Mar15-1046.xls",
the datalogger name is "5G0E3559". Use the lookup table "01-LookupTable.xlsx" to find the site codes for that datalogger, in the Site column of the table (Sheet 1).
Use those codes to execute the following SQL statement in MYSQLWorkbench: 
```
SELECT LocalDateTime FROM rush_valley.datavalues AS dv 
JOIN rush_valley.sites as s 
ON s.SiteID = dv.SiteID 
WHERE s.SiteCode IN ("Ru1BMP5", "Ru1BMP30", "Ru1BMPA", "Ru1BMNU")
ORDER BY LocalDateTime DESC LIMIT 1;
```
Replace "Ru1BMP5" and the other SiteCodes with the codes from the lookup table.
The result of the SQL query will be a timestamp of the most recent upload from that logger to the database. 
Values older than that should already be present, so to avoid duplicates we include the timestamp.
Use that timestamp (right-click it in Workbench, click "Open Value in Viewer", go to "Text" tab, copy and paste) as the -lt argument for data\_transfer.py.
The command to run the upload should look like this:
```
./data_transfer.py -lt '2015-06-15 00:00:00' -xls manual_files/rush150326/5G0E3559_27Mar15-1046.xls
```
Don't forget to enclose the timestamp in quotes and make sure the full path to the data file is present.

Use the -h option to view help or the -v option to view additional output
```
./data_transfer.py -h 

./data_transfer.py -v
```

