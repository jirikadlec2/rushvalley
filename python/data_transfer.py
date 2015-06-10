__author__ = 'Jiri'

# we use xlrd for reading the Excel lookup table file
import xlrd
import time
import json
import urllib2
import requests
import decagon
from converter import Converter


class Updater(object):

    def __init__(self):
        self.HYDROSERVER_USER = 'HIS_admin'
        self.HYDROSERVER_PASSWORD = 'password'
        self.HYDROSERVER_URL = 'http://worldwater.byu.edu/app/index.php/rushvalley/services/api/'
        self.dxd_folder = 'dxd'
        self.xlsfile = "01-LookupTable.xlsx"

    # checks is the file is a file or not
    def is_file(self, filename):
        try:
            with open(filename):
                pass
            return True
        except IOError as e:
            print "Unable to open file %s" % filename
            return None

    ##################################################
    # given a site code, gets the site id.           #
    # calls the GetSitesJSON function of the API     #
    # returns NONE if the site is not found.         #
    ##################################################
    def get_site_id(self, site_code):
        url = self.HYDROSERVER_URL + 'GetSitesJSON'
        r = requests.get(url)
        sites = r.json()
        for site in sites:
            if site['SiteCode'] == site_code:
                return site['SiteID']

        return None

    ##################################################
    # given a variable code, gets the variable id.   #
    # calls the GetVariablesJSON function of the API #
    # returns NONE if the variable is not found.     #
    ##################################################
    def get_variable_id(self, variable_code):
        url = self.HYDROSERVER_URL + 'GetVariablesJSON'
        r = requests.get(url)
        variables = r.json()
        for variable in variables:
            if variable['VariableCode'] == variable_code:
                return variable['VariableID']

        return None

    ####################################################################
    # reads the lookup table to find the association between the       #
    # sensor, response <---> variable_id, method_id                    #
    # uses the second sheet of the 01-Lookup lookup table Excel file   #
    ####################################################################
    def get_sensor_metadata(self, sensor):
        book = xlrd.open_workbook(self.xlsfile)
        sheets = book.sheets()
        sheet1 = sheets[1]
        nr = sheet1.nrows
        lookup = []
        for i in range(1, nr):
            sensor_code = sheet1.cell_value(i, 0)
            if sensor_code != sensor:
                continue

            variable_code = sheet1.cell_value(i, 2)

            #find the corresponding variable ID
            variable_id = self.get_variable_id(variable_code)
            if variable_id is None:
                print 'VariableID not found on server for VariableCode: ' + variable_code
                continue

            method_id = int(sheet1.cell_value(i, 3))
            response = sheet1.cell_value(i, 4)
            lookup.append({"sensor": sensor_code,
                           "variable": variable_code,
                           "variable_id": variable_id,
                           "method": method_id,
                           "response": response})
        return lookup

    #######################################################################
    # upload the data related to the sensor                               #
    # this function uses the HydroServer JSON API for uploading the data  #
    # it reads the data from the dxd file, converts the values, and calls #
    # the values function of the API using HTTP POST request.             #
    # The site_id, variable_id, method_id , and source_id must be valid   #
    # ID's that already exist in the database.                            #
    #######################################################################
    def sensor_upload(self, site_id, variable_id, method_id, source_id, dxd_file, port, sensor, resp):

        #reading the raw data from the dxd file
        raw_data = decagon.read_dxd(dxd_file, port)
        new_data = {
            "user": self.HYDROSERVER_USER,
            "password": self.HYDROSERVER_PASSWORD,
            "SiteID": site_id,
            "VariableID": variable_id,
            "MethodID": method_id,
            "SourceID": source_id,
            "values":[]
        }

        #converting the data from raw data to actual values
        nr = len(raw_data["dates"])
        c = Converter.create(sensor)
        for row in range(0, nr):
            raw_time = raw_data["dates"][row]
            raw_val = raw_data["vals"][row]
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(raw_time + 946684800))
            val = c.convert(resp, raw_val)
            new_data["values"].append((local_time, val))

        #the data is send in the JSON format as the body of the request
        payload = json.dumps(new_data)
        print payload

        url = self.HYDROSERVER_URL + 'values'
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')

        #upload the data to the web and check for any error status codes
        try:
            response = urllib2.urlopen(req, payload)
            status = json.load(response)
            print status

        except urllib2.HTTPError, e:
            print e.code
            print e.msg
            print e.headers
            print e.fp.read()


    #this script reads the lookup-table and for each row, gets the logger-port-response-site-variable-method information
    #this should include the SiteCode, SiteID, VariableID, MethodID
    ####################################################################
    # Uploads the data for all sites from the sensor.                  #
    ####################################################################
    def upload_data(self, sensor_name):

        #get the sensor metadata:
        #sensor, response, variable code, and method id
        sensor_metadata = self.get_sensor_metadata(sensor_name)

        #open the lookup table
        book = xlrd.open_workbook(self.xlsfile)
        sheets = book.sheets()
        sheet0 = sheets[0]
        nr = sheet0.nrows
        for i in range(1, nr):
            logger = sheet0.cell_value(i, 0)
            site_code = sheet0.cell_value(i, 1)
            port = int(sheet0.cell_value(i, 4))
            sensor = sheet0.cell_value(i, 5)

            #find the corresponding site ID
            site_id = self.get_site_id(site_code)
            if site_id is None:
                print 'SiteID not found on server for SiteCode: ' + site_code
                continue

            #find the right DXD file for the logger of this sensor
            dxd_file = '%s%s.dxd' % (self.dxd_folder, logger)
            if not self.is_file(dxd_file):
                continue

            #start the uploading
            if sensor == sensor_name:
                for md in sensor_metadata:
                    self.sensor_upload(site_id=site_id,
                                       variable_id=md["variable_id"],
                                       method_id=md["method"],
                                       source_id=1,
                                       resp=md["response"],
                                       dxd_file=dxd_file,
                                       port=port,
                                       sensor=sensor)


if __name__ == '__main__':

    #STEP 1: Get the data from DECAGON data loggers
    decagon.download_all('passwords.csv','dxd')

    #STEP 2: Upload the data to HydroServer
    u = Updater()
    u.dxd_folder = 'dxd/'
    u.upload_data('SRS')
    u.upload_data('PYR')
    u.upload_data('MPS-6')
    u.upload_data('GS3')