__author__ = 'Jiri'

#converts the dxd file to a sql file
import dxd
from converter import Converter
import time


def decagon_time(raw_time):
    return time.gmtime(raw_time + 946684800)

def decagon_time_local(raw_time):
    return time.localtime(raw_time + 946684800)


def sql_insert_values(raw_time, val, site_id, var_id, meth_id, src_id, qc_id):

    utc_time = decagon_time(raw_time)
    #TODO read the time zone from a settings file
    local_time = decagon_time_local(raw_time)
    utc_offset = -7

    sql_utc = time.strftime('%Y-%m-%d %H:%M:%S', utc_time)
    sql_local = time.strftime('%Y-%m-%d %H:%M:%S', local_time)

    return 'INSERT INTO datavalues(DataValue, UTCOffset, DateTimeUTC, LocalDateTime, \
SiteID, VariableID, CensorCode, MethodID, SourceID, QualityControlLevelID) \
VALUES (%s, %s, "%s", "%s", %s, %s, "nc", %s, %s, %s);' \
           % (val, utc_offset, sql_utc, sql_local, site_id, var_id, meth_id, src_id, qc_id)


def create_sql(dxd_file, port, sensor, response, sql_file):
    raw_data = dxd.read_dxd(dxd_file, port)
    #get the metadata - need to use lookup table
    site_id = 8
    var_id = 33
    meth_id = 68
    src_id = 1
    qc_id = 0

    f = open(sql_file,'w')

    nr = len(raw_data["dates"])
    c = Converter.create(sensor)
    for row in range(0, nr):
        raw_time = raw_data["dates"][row]
        raw_val = raw_data["vals"][row]

        val = c.convert(response, raw_val)
        sql = sql_insert_values(raw_time, val, site_id, var_id, meth_id, src_id, qc_id)
        f.write(sql)
        f.write('\n')
    f.close()


if __name__ == '__main__':
    dxd_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\5G0E3562new.dxd'
    sql_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\decagon_files\\test5.sql'
    create_sql(dxd_file, 4, 'GS3', 3, sql_file)
