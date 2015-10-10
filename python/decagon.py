#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Jiri'

from lxml import etree
import requests
import csv
import xlrd
import sys
import argparse
from dateutil.parser import parse
import time
import datetime
import unicodedata


########################################
# checks if the file is a file or not  #
########################################
def is_file(filename):
	try:
		with open(filename):
			pass
		return True
	except IOError as e:
		print "Unable to open file %s" % filename
		return None


##########################################################
# download all dxd files that are listed in the file	 #
# passwords.csv.				 #
##########################################################
def download_all(password_file, output_folder):
	with open(password_file) as csvfile:
		reader = csv.DictReader(csvfile)
		passwords = []
		for row in reader:
			print(row['DeviceID'], row['password'])
			passwords.append({'device_id':row['DeviceID'],'device_password':row['password']})
	print passwords
	for entry in passwords:
		download_dxd(entry['device_id'], entry['device_password'], 0, output_folder)
		print 'downloaded file: ' + entry['device_id']


##########################################################
# downloads the dxd file, given the device id, device	#
# password, and the MRID number.			 #
# if MRID is 0, then all of the data shall be downloaded #
##########################################################
def download_dxd(device_id, device_password, mr_id, output_folder):
	email = 'no-email@byu.edu'
	user_password = 'M-wuJf5!fu5554v'
	url = 'http://api.ech2odata.com/dfmp/dxd.cgi'
	report = 1
	file_name = output_folder + '/' + device_id + '.dxd'

	#set the mr_id from the file
	if is_file(file_name):
		mr_id = read_mrid(file_name)
		print('file_name: ' + file_name + ' mrid: ' + str(mr_id))

	payload = {'email': email, 'userpass': user_password, 'report': report, 'deviceid': device_id,
	  'devicepass': device_password, 'mrid': mr_id}
	r = requests.post(url, data=payload)

	with open(file_name, 'wb') as fd:
		for chunk in r.iter_content():
			fd.write(chunk)

##########################################################
# reads the MRID from the dxd file		#
# the MRID indicates the last download of the data	#
##########################################################
def read_mrid(dxd_file):
	txt = "no data found"
	doc = etree.parse(dxd_file)
	root = doc.getroot()
	for element in root.iter():
		if 'Data' in element.tag:
			mrid = int(element.get('rid'))
			return mrid
	return 0

##########################################################
# reads the dxd file and checks the response of the file #
# returns a dictionary with raw dates and raw values	 #
##########################################################
def read_dxd(dxd_file, port):
	txt = "no data found"
	doc = etree.parse(dxd_file)
	root = doc.getroot()
	for element in root.iter():
		if 'Data' in element.tag:
			nrow = int(element.get('scans'))
			print nrow
			txt = element.text

	#now parse txt to two lists dates, vals
	if txt == "no data found":
		return None
	result = {"dates": [], "vals": []}
	for line in txt.splitlines():
		if line.strip() == "":
			continue
		items = line.split(",")
		if port > len(items):
			raise ValueError('File %s does not have data from port %s' %(dxd_file, port))
		result["dates"].append(int(items[0]))
		result["vals"].append(int(items[port]))
	return result

#############################################################
# Opens the lookup file and gets the general name, specific #
# name, and variable code for the variable requested		#
#############################################################
def get_variable_data(var_id, lookup_file):
	book = xlrd.open_workbook(lookup_file)
	var_sheet = book.sheet_by_index(2)

	row_num = 2 #values start in third row
	result = {
		'gen_name': "",
		'spec_name': "",
		'var_code': "",
		'var_id': var_id
	}
	header_row = var_sheet.row(0)
	while row_num < 18: #there are only 18 rows in the file
		row = var_sheet.row(row_num)
		row_num += 1
		if row[3].value == var_id:
			data_array = []
			for i in range (0, 3):
				cell_val = row[i].value
				cell_val = unicodedata.normalize('NFKD', cell_val).encode('ascii','ignore')
				data_array.append(cell_val)
			result['gen_name'] = data_array[0]
			result['spec_name'] = data_array[1]
			result['var_code'] = data_array[2]
			break
	return result

#############################################################
# Checks whether the given site, logger, and port are a 	#
# valid combination											#
#############################################################
def validate_site(site_code, logger_name, port, lookup_file):
	book = xlrd.open_workbook(lookup_file)
	main_sheet = book.sheet_by_index(0)
	row_num = 1 #data starts on second row
	
	while row_num < 105: #there are 105 rows
		row = main_sheet.row(row_num)
		row_num += 1
		if row[0].value == logger_name and row[1].value == site_code and row[4].value == port:
			return True
	return False

#############################################################
# Reads the xls file and checks the response of the file. 	#
# Returns a dictionary with raw dates and raw values.	 	#
# Loops through the rows and store the values in dictionary.#
# Loops by getting the values of the first column. They		#
# should be the timestamps, so if one is not set, it should #
# the n+1, and loop is done. Assumes that the first three 	#
# rows are metadata											#
#############################################################
def read_xls(var_id, site_code, xls_file, port, old_timestamp, logger_name, lookup_file):
	var_id = float(unicodedata.normalize('NFKD', var_id).encode('ascii','ignore'))
	if not validate_site(site_code, logger_name, port, lookup_file):
		print "Invalid site, port combination with site " + str(site_code) + " and port " + str(port)
		return
	variable_data = get_variable_data(var_id, lookup_file)
	if variable_data['gen_name'] == "":
		print "No data for variable " + str(var_id) + " in logger: " + str(logger)
		return
	book = xlrd.open_workbook(xls_file)
	sheet0 = book.sheet_by_index(0)
	result = [] 

	row_num = 0
	row = sheet0.row(row_num)
	header_rows = []
	keep_reading = True

	while keep_reading:
		if row_num < 3: #the first three rows are metadata
			header_rows.append(row)
		else:
			raw_date = row[0].value

			if raw_date != None and raw_date != "":
				year, month, day, hour, minute, second = xlrd.xldate_as_tuple(raw_date, book.datemode)
				date_obj = datetime.datetime(year, month, day, hour, second)

				#don't include old values
				if old_timestamp == "none" or date_obj > old_timestamp:
					date = str(date_obj)
					index = -10
					for i in range(1, len(row)):
						line0 = unicodedata.normalize('NFKD', header_rows[0][i].value).encode('ascii','ignore')
						line1 = unicodedata.normalize('NFKD', header_rows[1][i].value).encode('ascii','ignore')
						line2 = unicodedata.normalize('NFKD', header_rows[2][i].value).encode('ascii','ignore')
						local_port = line0.split()[1]
						if "MPS-2" in line1:
							line1 = line1.replace("MPS-2", "MPS-6")

						if int(local_port) == port and line1 == variable_data['gen_name'] and line2 == variable_data['spec_name']:
							index = i
							break
					if index == -10:
						print "No data for variable " + str(var_id) + " in logger: " + str(logger_name)
						break
					pair = date, row[index].value
					result.append(pair)

		try:
			row_num += 1
			row = sheet0.row(row_num)
		except:
			keep_reading = False
	return result
	

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = "Download Datalogger data from decagon site in .dxd format.\n" +
		"By default uses passwords.csv for password lookup and outputs to dxd directory, but these may be overridden.")
	parser.add_argument("passwords", nargs='?', type=argparse.FileType('r'), default="passwords.csv",
		help="file to look up passwords for download")
	parser.add_argument("out_directory", nargs='?', default="dxd", help="directory of .dxd files to which the " + 
		"downloaded data will be saved.")
	namespace = parser.parse_args()
	download_all(namespace.passwords.name, namespace.out_directory)
