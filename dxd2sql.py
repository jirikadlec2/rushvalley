__author__ = 'Jiri'

#converts the dxd file to a sql file
import dxd
from converter import Converter
import time


class SQLManager(object):

    def __init__(self, site, var, meth):
        self.site_id = site
        self.var_id = var
        self.meth_id = meth
        self.src_id = 1
        self.qc_id = 0

    utc_offset = -7


    def decagon_time_local(self, raw_time):
        return time.gmtime(raw_time + 946684800)


    def decagon_time_utc(self, raw_time):
        return time.gmtime(raw_time + 946684800 - self.utc_offset*3600)


    def insert_values(self, raw_time, val, site_id, var_id, meth_id, src_id, qc_id):

        utc_time = self.decagon_time_utc(raw_time)
        local_time = self.decagon_time_local(raw_time)

        sql_utc = time.strftime('%Y-%m-%d %H:%M:%S', utc_time)
        sql_local = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

        return 'INSERT INTO datavalues(DataValue, UTCOffset, DateTimeUTC, LocalDateTime, \
    SiteID, VariableID, CensorCode, MethodID, SourceID, QualityControlLevelID) \
    VALUES (%s, %s, "%s", "%s", %s, %s, "nc", %s, %s, %s);' \
               % (val, self.utc_offset, sql_utc, sql_local, site_id, var_id, meth_id, src_id, qc_id)


    def create_sql(self, dxd_file, port, sensor, response, sql_file):
        raw_data = dxd.read_dxd(dxd_file, port)

        f = open(sql_file,'w')

        nr = len(raw_data["dates"])
        c = Converter.create(sensor)
        for row in range(0, nr):
            raw_time = raw_data["dates"][row]
            raw_val = raw_data["vals"][row]

            val = c.convert(response, raw_val)
            sql = self.insert_values(raw_time, val, self.site_id, self.var_id,
                                     self.meth_id, self.src_id, self.qc_id)
            f.write(sql)
            f.write('\n')
        f.close()


if __name__ == '__main__':
    dxd_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\5G0E3562new.dxd'
    sql_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\test11.sql'
    m = SQLManager(site=8, var=33, meth=68)
    m.create_sql(dxd_file, port=4, sensor='GS3', response=3, sql_file=sql_file)
