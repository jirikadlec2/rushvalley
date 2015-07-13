#! /bin/bash

cd /home/WWO_Admin/decagonUpload/

#get the current date/time for the logfile
now=$(date)
#parse out whitespace
now_mod=${now// /_}
now_mod=${now_mod//__/_}
log=logfiles/$now_mod"_log.log"

#run the transfer and write output to log 
./data_transfer.py $now >> $log 

#clean up the .dxd files generated
cd dxd/ 
rm *.dxd

#clean up the logfiles if they're becoming cluttered (only 14 allowed at a time)
cd ../
./clean_logs.py

