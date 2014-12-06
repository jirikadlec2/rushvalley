__author__ = 'Jiri'

import xlrd
import pymysql
import dxd2sql


class Updater(object):

    def __init__(self):
        self.db_host = 'worldwater.byu.edu'
        self.db_user = 'WWO_Admin'
        self.db_pass = 'isaiah4118'
        self.db_db = 'RushValley'

    #rather use GetSites() method here, then we don't need password.
    def get_site_id(self, site_code):
        res = None
        conn = pymysql.connect(host=self.db_host, port=3306, user=self.db_user, passwd=self.db_pass, db=self.db_db)
        cur = conn.cursor()
        qry = 'SELECT SiteID FROM sites WHERE SiteCode = "%s"' % site_code
        cur.execute(qry)
        r = cur.fetchone()
        if r:
            res = int(r[0])

        cur.close()
        conn.close()
        return res

    #gets the latest dataValue from the database
    def get_last_db_time(self, site_id, var_id, meth_id):
        res = None
        conn = pymysql.connect(host=self.db_host, port=3306, user=self.db_user, passwd=self.db_pass, db=self.db_db)
        cur = conn.cursor()
        qry = 'SELECT EndDateTimeUTC FROM seriescatalog WHERE SiteID = %s AND VariableID = %s AND MethodID = %s' \
              % (site_id, var_id, meth_id)
        cur.execute(qry)
        r = cur.fetchone()
        if r:
            res = r[0]
        cur.close()
        conn.close()
        return res

    def is_file(self, filename):
        try:
            with open(filename) as file:
                pass
            return True
        except IOError as e:
            print "Unable to open file %s" % filename
            return None

    def sensor_sql(self, site, var, meth, dxd, port, sensor, resp, sql_file):
        m = dxd2sql.SQLManager(site=site, var=var, meth=meth)
        db_time = self.get_last_db_time(site, var, meth)
        m.create_sql(dxd, port=port, sensor=sensor, response=resp, sql_file=sql_file,
                           begin_time=db_time, append=True)

    #this script reads the lookup-table and for each row, gets the logger-port-response-site-variable-method information
    #this should include the SiteCode, SiteID, VariableID, MethodID
    def read_lookup(self, xlsfile, out_dir, sensor_name):
        book = xlrd.open_workbook(xlsfile)
        sheets = book.sheets()
        sheet0 = sheets[0]
        nr = sheet0.nrows
        nc = sheet0.ncols
        for i in range(1, nr):
            logger = sheet0.cell_value(i, 0)
            site_code = sheet0.cell_value(i, 1)
            port = int(sheet0.cell_value(i, 4))
            sensor = sheet0.cell_value(i, 5)

            dxd_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\dxd\\%s.dxd' % logger
            if not self.is_file(dxd_file):
                continue

            sql_file = '%s\\%s.sql' % (out_dir, sensor)
            site_id = self.get_site_id(site_code)
            if site_id is None:
                print 'site not found in db: %s' % site_code
                continue

            if sensor == sensor_name:
                if sensor == 'MPS-6':
                    #water potential
                    self.sensor_sql(site=site_id, var=20, meth=62, resp=1, dxd=dxd_file,
                                    port=port, sensor=sensor, sql_file=sql_file)

                    #temperature
                    self.sensor_sql(site=site_id, var=22, meth=63, resp=2, dxd=dxd_file,
                                    port=port, sensor=sensor, sql_file=sql_file)

                elif sensor == 'GS3':
                    #soil moisture
                    self.sensor_sql(site=site_id, var=27, meth=66, resp=1, dxd=dxd_file,
                                    port=port, sensor=sensor, sql_file=sql_file)

                    #temperature
                    self.sensor_sql(site=site_id, var=29, meth=67, resp=2, dxd=dxd_file,
                                    port=port, sensor=sensor, sql_file=sql_file)

                    #conductivity
                    self.sensor_sql(site=site_id, var=33, meth=68, resp=3, dxd=dxd_file,
                                    port=port, sensor=sensor, sql_file=sql_file)

                elif sensor == 'SRS':
                    #Red
                    self.sensor_sql(site=site_id, var=23, meth=64, resp=1, dxd=dxd_file,
                                    port=port, sensor='SRS-Nr', sql_file=sql_file)

                    #Nir
                    self.sensor_sql(site=site_id, var=25, meth=65, resp=2, dxd=dxd_file,
                                    port=port, sensor='SRS-Nr', sql_file=sql_file)

                    #NDVI
                    self.sensor_sql(site=site_id, var=43, meth=72, resp=3, dxd=dxd_file,
                                    port=port, sensor='SRS-Nr', sql_file=sql_file)

                elif sensor == 'PYR':
                    self.sensor_sql(site=site_id, var=44, meth=73, resp=1, dxd=dxd_file,
                                    port=port, sensor='PYR', sql_file=sql_file)





if __name__ == '__main__':
    xlsfile = "C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\01-LookupTable.xlsx"
    u = Updater()
    #t = u.get_last_db_time(8, 22, 63)
    #print type(t)
    out_dir = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\sql'
    u.read_l ookup(xlsfile, out_dir, 'MPS-6')
    u.read_lookup(xlsfile, out_dir, 'GS3')
    u.read_lookup(xlsfile, out_dir, 'SRS')
    u.read_lookup(xlsfile, out_dir, 'PYR')