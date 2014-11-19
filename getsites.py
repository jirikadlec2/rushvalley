__author__ = 'Jiri'

import ulmo
import pymysql

conn = pymysql.connect(host='worldwater.byu.edu', port=3306, user='WWO_Admin', passwd='isaiah4118', db='dr')
cur = conn.cursor()


def get_site_id(site_code, conn):
    qry = 'SELECT DISTINCT SiteID FROM seriescatalog WHERE SiteCode = "%s"' % site_code
    cur.execute(qry)
    r = cur.fetchone()
    if r:
        return r[0]
    else:
        return 10000 + int(site_code)

#get_site_id("40001", conn)
sql_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\dominican.sql'
f = open(sql_file,'w')

wsdl = "http://byuhydro.byu.edu/drdata/cuahsi_1_0.asmx?WSDL"
sites = ulmo.cuahsi.wof.get_sites(wsdl)
for code, obj in sites.iteritems():
    print code
    print obj
    code2 = obj['code']
    id = get_site_id(code2, conn)
    sql = 'INSERT INTO sites(SiteID, SiteCode, SiteName, Latitude, \
    Longitude, Elevation_m, LatLongDatumID) \
    VALUES (%s, %s, "%s", %s, %s, %s, %s);' \
          % (id, code2, obj["name"], obj['location']["latitude"], obj['location']["longitude"], obj["elevation_m"], 3)
    f.write(sql)
    f.write('\n')

    print sql

f.close()

