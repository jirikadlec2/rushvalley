__author__ = 'Jiri'

import xlrd
import os
import datetime
import pymysql

def findFile(directory, logger):
    found = [i for i in os.listdir(directory) if logger in i and '.xls' in i]
    #check that file exist
    if len(found) > 0:
        return os.path.join(directory, found[0])


#input: tab separated text file
#output: time series of the data values
def readData(directory, logger, port, sensor, response):
    loggerfile = findFile(directory, logger)
    book = xlrd.open_workbook(loggerfile)
    sheets = book.sheets()
    sheet0 = sheets[0]
    nr = sheet0.nrows - 1
    nc = sheet0.ncols - 1
    print nr

    #todo: find which column according to port, sensor, response
    cellnum = 2
    #1st row
    dates = [None] * nr
    vals = [None] * nr
    for rownum in range(3, nr):
        print sheet0.row(nr)
        dat = sheet0.cell_value(rownum, 0)
        dat_dt = datetime.datetime(*xlrd.xldate_as_tuple(dat, book.datemode))
        print sheet0.cell_value(rownum, 0)
        print dat_dt
        dates[rownum] = dat_dt
        vals[rownum] = sheet0.cell_value(rownum, cellnum)
    return dates, vals

def createSQL(dates, values, siteCode, variableCode, methodName):
    #STEPS:
    #fetch siteID from db

    #fetch variableID from db

    #fetch methodID from db

    #generate .sql file from db

if __name__ == '__main__':
    (dats, vals) = readData('C:\\dev\\github\\rushvalley\\RushValleyoct152014','5G0E3559', 1, 'MPS-6','Temperature')
    for i in range(0,100):
        print str(dats[i]) + ' ' + str(vals[i])