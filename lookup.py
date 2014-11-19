__author__ = 'Jiri'

import xlrd
import pymysql
import dxd2sql

#rather use GetSites() method here, then we don't need password.
def get_site_id(site_code):
    res = None
    conn = pymysql.connect(host='worldwater.byu.edu', port=3306, user='USERNAME', passwd='PASSWORD', db='RushValley')
    cur = conn.cursor()
    qry = 'SELECT SiteID FROM sites WHERE SiteCode = "%s"' % site_code
    cur.execute(qry)
    r = cur.fetchone()
    if r:
        res = int(r[0])

    cur.close()
    conn.close()
    return res


def is_file(filename):
    try:
        with open(filename) as file:
            pass
        return True
    except IOError as e:
        print "Unable to open file %s" % filename
        return None


#this script reads the lookup-table and for each row, gets the logger-port-response-site-variable-method information
#this should include the SiteCode, SiteID, VariableID, MethodID
def read_lookup(xlsfile, out_dir, sensor_name):
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
        if not is_file(dxd_file):
            continue

        if sensor == sensor_name:
            if sensor == 'MPS-6':
                site_id = get_site_id(site_code)
                sql_file = out_dir + '\\%s.sql' % sensor

                #water potential
                vari_id = 20
                meth_id = 62
                resp = 1
                m = dxd2sql.SQLManager(site=site_id, var=vari_id, meth=meth_id)
                m.create_sql(dxd_file, port=port, sensor=sensor, response=resp, sql_file=sql_file, append=True)

                #temperature
                vari_id = 22
                meth_id = 63
                resp = 2
                m = dxd2sql.SQLManager(site=site_id, var=vari_id, meth=meth_id)
                m.create_sql(dxd_file, port=port, sensor=sensor, response=resp, sql_file=sql_file, append=True)

            elif sensor == 'GS3':
                site_id = get_site_id(site_code)
                sql_file = out_dir + '\\%s.sql' % sensor

                #soil moisture
                m = dxd2sql.SQLManager(site=site_id, var=27, meth=66)
                m.create_sql(dxd_file, port=port, sensor=sensor, response=1, sql_file=sql_file, append=True)

                #temperature
                m = dxd2sql.SQLManager(site=site_id, var=29, meth=67)
                m.create_sql(dxd_file, port=port, sensor=sensor, response=2, sql_file=sql_file, append=True)

                #conductivity
                m = dxd2sql.SQLManager(site=site_id, var=33, meth=68)
                m.create_sql(dxd_file, port=port, sensor=sensor, response=3, sql_file=sql_file, append=True)

            elif sensor == 'SRS':
                site_id = get_site_id(site_code)

                if site_id is None:
                    print 'site not found in db: %s' % site_code
                    continue

                sql_file = out_dir + '\\%s.sql' % sensor

                #Red
                m = dxd2sql.SQLManager(site=site_id, var=23, meth=64)
                m.create_sql(dxd_file, port=port, sensor='SRS-Nr', response=1, sql_file=sql_file, append=True)
                #Nir
                m = dxd2sql.SQLManager(site=site_id, var=25, meth=65)
                m.create_sql(dxd_file, port=port, sensor='SRS-Nr', response=2, sql_file=sql_file, append=True)
                #NDVI
                m = dxd2sql.SQLManager(site=site_id, var=43, meth=72)
                m.create_sql(dxd_file, port=port, sensor='SRS-Nr', response=3, sql_file=sql_file, append=True)





if __name__ == '__main__':
    xlsfile = "C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\01-LookupTable.xlsx"
    read_lookup(xlsfile, 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\sql', 'SRS')