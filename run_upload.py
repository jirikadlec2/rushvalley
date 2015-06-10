__author__ = 'Jiri'

import xlrd
import time
import json
import urllib2
import dxd
from converter import Converter


class Updater(object):

    def __init__(self):
        self.hydroserver_user = 'HIS_admin'
        self.hydroserver_password = 'password'
        self.dxd_folder = 'dxd'
        self.HYDROSERVER_URL = 'http://worldwater.byu.edu/app/index.php/rushvalley/services/api/values/'

    # checks is the file is a file or not
    def is_file(self, filename):
        try:
            with open(filename):
                pass
            return True
        except IOError as e:
            print "Unable to open file %s" % filename
            return None


    #reads the association between the sensor, response, variable code, and method id
    def sensor_lookup(self, sensor):
        book = xlrd.open_workbook(xlsfile)
        sheets = book.sheets()
        sheet1 = sheets[1]
        nr = sheet1.nrows
        lookup = []
        for i in range(1, nr):
            sensor_code = sheet1.cell_value(i, 0)
            if sensor_code != sensor:
                continue

            variable_code = sheet1.cell_value(i, 2)
            method_id = int(sheet1.cell_value(i, 3))
            response = sheet1.cell_value(i, 4)
            lookup.append({"sensor": sensor_code,
                           "variable": variable_code,
                           "method": method_id,
                           "response": response})
        return lookup


    #now upload the data related to the sensor
    def sensor_upload(self, site, var, meth, dxd_file, port, sensor, resp):
        raw_data = dxd.read_dxd(dxd_file, port)
        new_data = {
            "user": self.hydroserver_user,
            "password": self.hydroserver_password,
            "sitecode": site,
            "variablecode": var, #need to read from lookup table
            "methodid": meth,
            "sourceid": 1,
            "values":[]
        }
        nr = len(raw_data["dates"])
        c = Converter.create(sensor)
        for row in range(0, nr):
            raw_time = raw_data["dates"][row]
            raw_val = raw_data["vals"][row]
            local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(raw_time + 946684800))
            val = c.convert(resp, raw_val)
            new_data["values"].append((local_time, val))

        postdata = json.dumps(new_data)
        print postdata

        url = 'http://worldwater.byu.edu/interactive/rushvalley/services/index.php/upload/values'
        req = urllib2.Request(url)
        req.add_header('Content-Type', 'application/json')

        #uploading to the web
        try:
            response = urllib2.urlopen(req, postdata)
            status = json.load(response)
            print status

        except urllib2.HTTPError, e:
            print e.code
            print e.msg
            print e.headers
            print e.fp.read()


    #this script reads the lookup-table and for each row, gets the logger-port-response-site-variable-method information
    #this should include the SiteCode, SiteID, VariableID, MethodID
    def read_lookup(self, xlsfile, out_dir, sensor_name):

        #get the sensor metadata
        sensor_metadata = self.sensor_lookup(sensor_name)

        book = xlrd.open_workbook(xlsfile)
        sheets = book.sheets()
        sheet0 = sheets[0]
        nr = sheet0.nrows
        for i in range(1, nr):
            logger = sheet0.cell_value(i, 0)
            site_code = sheet0.cell_value(i, 1)
            port = int(sheet0.cell_value(i, 4))
            sensor = sheet0.cell_value(i, 5)

            dxd_file = '%s%s.dxd' % (self.dxd_folder, logger)
            if not self.is_file(dxd_file):
                continue

            if sensor == sensor_name:
                for md in sensor_metadata:
                    self.sensor_upload(site=site_code,
                                       var=md["variable"],
                                       meth=md["method"],
                                       resp=md["response"],
                                       dxd_file=dxd_file,
                                       port=port,
                                       sensor=sensor)


if __name__ == '__main__':
    xlsfile = "C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\01-LookupTable.xlsx"
    u = Updater()
    u.dxd_folder = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\dxd\\'
    out_dir = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\sql'

    u.read_lookup(xlsfile, out_dir, 'GS3')
    u.read_lookup(xlsfile, out_dir, 'SRS')
    u.read_lookup(xlsfile, out_dir, 'PYR')