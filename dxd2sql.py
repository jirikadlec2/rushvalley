__author__ = 'Jiri'

#converts the dxd file to a sql file
import dxd
from converter import Converter
import time
import calendar


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


    def insert_values(self, utc_time, local_time, val, site_id, var_id, meth_id, src_id, qc_id):

        sql_utc = time.strftime('%Y-%m-%d %H:%M:%S', utc_time)
        sql_local = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

        return 'INSERT INTO datavalues(DataValue, UTCOffset, DateTimeUTC, LocalDateTime, \
    SiteID, VariableID, CensorCode, MethodID, SourceID, QualityControlLevelID) \
    VALUES (%s, %s, "%s", "%s", %s, %s, "nc", %s, %s, %s);' \
               % (val, self.utc_offset, sql_utc, sql_local, site_id, var_id, meth_id, src_id, qc_id)


    def create_sql(self, dxd_file, port, sensor, response, sql_file, begin_time=None, append=False):
        raw_data = dxd.read_dxd(dxd_file, port)
        if raw_data is None:
            return None

        if append:
            f = open(sql_file, 'a')
        else:
            f = open(sql_file,'w')

        #begin time to prevent insertion of duplicate values
        if begin_time is not None:
            begin_timestamp = calendar.timegm(begin_time.utctimetuple())

        nr = len(raw_data["dates"])
        c = Converter.create(sensor)
        for row in range(0, nr):

            raw_time = raw_data["dates"][row]
            raw_val = raw_data["vals"][row]
            utc_time = self.decagon_time_utc(raw_time)
            local_time = self.decagon_time_local(raw_time)

            utc_timestamp = time.mktime(utc_time)

            if begin_time is not None:
                if utc_timestamp <= begin_timestamp:
                    continue

            val = c.convert(response, raw_val)
            sql = self.insert_values(utc_time, local_time, val, self.site_id, self.var_id,
                                     self.meth_id, self.src_id, self.qc_id)
            f.write(sql)
            f.write('\n')
        f.close()
