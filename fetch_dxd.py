__author__ = 'Jiri'

import xlrd
from lxml import etree
from os import listdir
from os.path import isfile, join


def get_dxd_passwords(password_file):
    book = xlrd.open_workbook(password_file)
    sheets = book.sheets()
    sheet0 = sheets[0]
    nr = sheet0.nrows
    nc = sheet0.ncols
    password_list = []
    for i in range(1, nr):
        logger = sheet0.cell_value(i, 0)
        password = sheet0.cell_value(i, 1)
        password_list.append({"logger": logger, "password": password})
    return password_list


def read_mrid(dxd_file):
    doc = etree.parse(dxd_file)
    root = doc.getroot()
    for element in root.iter():
        if 'Data' in element.tag:
            rid = int(element.get('rid'))
            return rid
    return 0


def create_download_script(password_file, dxd_folder, out_file):

    email = 'no-email@byu.edu'
    userpass = 'M-wuJf5!fu5554v'
    url = 'http://api.ech2odata.com/dfmp/dxd.cgi'

    sh = open(out_file, 'w')

    dxd_info = get_dxd_passwords(password_file)

    for dxd in dxd_info:
        logger = dxd['logger']
        password = dxd['password']
        dxd_file = '%s/%s.dxd'% (dxd_folder, logger)
        print dxd_file
        mrid = read_mrid(dxd_file)
        cmd = "curl --trace tracelog.txt -A BYU -d 'email=%s' -d 'userpass=%s' -d 'deviceid=%s' -d 'devicepass=%s' \
-d 'report=1' -d 'mrid=%s' '%s' > '%s.dxd'" % (email, userpass, logger, password, mrid, url, logger)
        print cmd
        sh.write(cmd)
        sh.write('\n')
    sh.close()


if __name__ == '__main__':
    password_file = 'C:\\jiri\\Dropbox\\BYU\\hydroinformatics\\project\\passwords.xlsx'
    passwords = get_dxd_passwords(password_file)
    print passwords
    script = create_download_script(password_file, 'C:/jiri/Dropbox/BYU/hydroinformatics/project/dxd',
                                    'C:/jiri/Dropbox/BYU/hydroinformatics/project/decagon.sh')