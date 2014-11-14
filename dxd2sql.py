__author__ = 'Jiri'

#converts the dxd file to a sql file
import time
import pytz
import dxd
import converter

def sql_insert_values(raw_time, val, site_id, var_id, meth_id, src_id, qc_id):

    utc_time = dxd.decagon_time(raw_time)
    #TODO read the time zone from a settings file
    local_time = dxd.decagon_time_local(raw_time)
    utc_offset = -7

    sql_utc = time.strftime('%Y-%m-%d %H:%M:%S', utc_time)
    sql_local = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

    return 'INSERT INTO datavalues(DataValue, UTCOffset, DateTimeUTC, LocalDateTime, \
SiteID, VariableID, CensorCode, MethodID, SourceID, QualityControlLevelID) \
VALUES (%s, %s, "%s", "%s", %s, %s, "nc", %s, %s, %s);' \
           % (val, utc_offset, sql_utc, sql_local, site_id, var_id, meth_id, src_id, qc_id)


def create_sql(dxd_file, port, sensor, response):
    raw_data = dxd.read_dxd(dxd_file, port)
    nr = len(raw_data)
    for row in range(0, nr):
        print row

if __name__ == '__main__':
    raw_time = 456418800
    sql = sql_insert_values(raw_time, 123, 1, 1, 1, 1, 1)
    print sql