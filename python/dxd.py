__author__ = 'Jiri'

from lxml import etree
from os import listdir
from os.path import isfile, join
import requests
import csv


##########################################################
# download all dxd files that are listed in the file     #
# passwords.csv.                                         #
##########################################################
def download_all(password_file, output_folder):
    with open(password_file) as csvfile:
        reader = csv.DictReader(csvfile)
        passwords = []
        for row in reader:
            print(row['DeviceID'], row['password'])
            passwords.append({'device_id':row['DeviceID'],'device_password':row['password']})
    print passwords
    for entry in passwords:
        download_dxd(entry['device_id'], entry['device_password'], 0, output_folder)
        print 'downloaded file: ' + entry['device_id']


##########################################################
# downloads the dxd file, given the device id, device    #
# password, and the MRID number.                         #
# if MRID is 0, then all of the data shall be downloaded #
##########################################################
def download_dxd(device_id, device_password, mr_id, output_folder):
    email = 'no-email@byu.edu'
    user_password = 'M-wuJf5!fu5554v'
    url = 'http://api.ech2odata.com/dfmp/dxd.cgi'
    report = 1
    payload = {'email': email, 'userpass': user_password, 'report': report, 'deviceid': device_id,
               'devicepass': device_password, 'mrid': mr_id}
    r = requests.post(url, data=payload)
    file_name = output_folder + '/' + device_id + '.dxd'
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content():
            fd.write(chunk)

##########################################################
# reads the dxd file and checks the response of the file #
# returns a dictionary with raw dates and raw values     #
##########################################################
def read_dxd(dxd_file, port):
    txt = "no data found"
    doc = etree.parse(dxd_file)
    root = doc.getroot()
    for element in root.iter():
        if 'Data' in element.tag:
            nrow = int(element.get('scans'))
            print nrow
            txt = element.text

    #now parse txt to two lists dates, vals
    if txt == "no data found":
        return None
    result = {"dates": [], "vals": []}
    for line in txt.splitlines():
        if line.strip() == "":
            continue
        items = line.split(",")
        if port > len(items):
            raise ValueError('File %s does not have data from port %s' %(dxd_file, port))
        result["dates"].append(int(items[0]))
        result["vals"].append(int(items[port]))
    return result


if __name__ == '__main__':
    download_all('passwords.csv','dxd')
    #download_dxd('5G0E3562', 'cicu-lywoy', 0)
    #txt = read_dxd('C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\5G0E3562new.dxd', 1)
    #print txt["dates"]