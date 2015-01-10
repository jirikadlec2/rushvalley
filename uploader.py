import dxd
from converter import Converter
import time
import calendar


class Uploader(object):
    def upload_sensor(dxd_file, port, sensor, site, var, meth):
        values = dxd.read_dxd(dxd_file, port)
        print values


if __name__ == '__main__':
    xlsfile = "C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\01-LookupTable.xlsx"
    u = Uploader()
    #t = u.get_last_db_time(8, 22, 63)
    #print type(t)
    out_dir = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\sql'
    u.read_lookup(xlsfile, out_dir, 'MPS-6')
    u.read_lookup(xlsfile, out_dir, 'GS3')
    u.read_lookup(xlsfile, out_dir, 'SRS')
    u.read_lookup(xlsfile, out_dir, 'PYR')