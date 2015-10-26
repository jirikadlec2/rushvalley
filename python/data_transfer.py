#! /usr/bin/env python
__author__ = 'Jiri'

# we use xlrd for reading the Excel lookup table file
import sys
import xlrd
import time
import json
import urllib2
import requests
import decagon
import argparse
import datetime
from dateutil.parser import parse
from converter import Converter


class Updater(object):

	def __init__(self):
		self.HYDROSERVER_USER = 'HIS_admin'
		self.HYDROSERVER_PASSWORD = 'password'
		self.HYDROSERVER_URL = 'http://worldwater.byu.edu/app/index.php/rushvalley/services/api/'
		self.dxd_folder = 'dxd'
		self.xlsfile = "01-LookupTable.xlsx"
		self.old_timestamp = "none"
		self.verbose = False
		self.no_upload = False

	# checks if the file is a file or not
	def is_file(self, filename):
		try:
			with open(filename):
				pass
			return True
		except IOError as e:
			print "Unable to open file %s" % filename
			return None

	##################################################
	# given a site code, gets the site id.		   #
	# calls the GetSitesJSON function of the API	 #
	# returns NONE if the site is not found.		 #
	##################################################
	def get_site_id(self, site_code):
		url = self.HYDROSERVER_URL + 'GetSitesJSON'
		r = requests.get(url)
		sites = r.json()
		for site in sites:
			if site['SiteCode'] == site_code:
				return site['SiteID']

		return None

	##################################################
	# given a variable code, gets the variable id.   #
	# calls the GetVariablesJSON function of the API #
	# returns NONE if the variable is not found.	 #
	##################################################
	def get_variable_id(self, variable_code):
		url = self.HYDROSERVER_URL + 'GetVariablesJSON'
		r = requests.get(url)
		variables = r.json()
		for variable in variables:
			if variable['VariableCode'] == variable_code:
				return variable['VariableID']

		return None

	####################################################################
	# reads the lookup table to find the association between the	   #
	# sensor, response <---> variable_id, method_id					#
	# uses the second sheet of the 01-Lookup lookup table Excel file   #
	####################################################################
	def get_sensor_metadata(self, sensor):
		book = xlrd.open_workbook(self.xlsfile)
		sheets = book.sheets()
		if self.verbose:
			print "filename" + self.xlsfile
		sheet1 = sheets[1]
		nr = sheet1.nrows
		lookup = []
		for i in range(1, nr):
			sensor_code = sheet1.cell_value(i, 0)
			if sensor_code != sensor:
				continue

			variable_code = sheet1.cell_value(i, 2)
			#find the corresponding variable ID
			variable_id = self.get_variable_id(variable_code)
			if variable_id is None:
				if self.verbose:
					print 'VariableID not found on server for VariableCode: ' + variable_code
				continue

			method_id = int(sheet1.cell_value(i, 3))
			response = sheet1.cell_value(i, 4)
			lookup.append({"sensor": sensor_code,
						   "variable": variable_code,
						   "variable_id": variable_id,
						   "method": method_id,
						   "response": response})
		return lookup
	
	#########################################################################
	# This function reads the values to upload from a local user-provided	#
	# xls file and returns them.											#
	#########################################################################
	def read_local_values(self, port):
		book = xlrd.open_workbook(self.manual_upload_file)
		sheets = book.sheets()
		sheet0 = sheets[0]
		nr = sheet0.nrows
		for i in range(1, nr):
			logger = sheet0.cell_value(i, 0)

		

	#########################################################################
	# Upload the data related to the sensor.						   		#
	# This function uses the HydroServer JSON API for uploading the data.	#
	# If being used for manual upload, it reads the data from a local		#
	# user-provided xls file. Otherwise, it reads the data from the dxd		#
	# file, converts the values, and calls the values function of the API	#
	# using HTTP POST request.									 			#
	# The site_id, variable_id, method_id , and source_id must be valid   	#
	# ID's that already exist in the database.								#
	#########################################################################
	def sensor_upload(self, site_id, site_code, variable_id, method_id, source_id, upload_file, port, sensor, resp, logger):
		new_data = {
				"user": self.HYDROSERVER_USER,
				"password": self.HYDROSERVER_PASSWORD,
				"SiteID": site_id,
				"VariableID": variable_id,
				"MethodID": method_id,
				"SourceID": source_id,
				"values":[]
		}
		#reading the new data from the dxd file
		if (self.manual_upload_file != None):
			new_data['values'] =  decagon.read_xls(variable_id, site_code, u.manual_upload_file.name, port, self.old_timestamp, logger, self.xlsfile)
		else:
			raw_data = decagon.read_dxd(upload_file, port)
		
			#converting the data from raw data to actual values
			nr = len(raw_data["dates"])
			c = Converter.create(sensor)
			for row in range(0, nr):
				raw_time = raw_data["dates"][row]
				raw_val = raw_data["vals"][row]
				local_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(raw_time + 946684800))
				local_time_obj = parse(local_time)
				val = c.convert(resp, raw_val)
				#only upload the values more recent than the old latest update
				if self.old_timestamp != "none":
					if local_time_obj > self.old_timestamp:
						new_data["values"].append((local_time, val))
				else:
					print "Error: No timestamp given for latest update. Rerun with timestamp"
					sys.exit()
		#if there's no data, return
		if len(new_data["values"]) <= 0:
			if self.verbose:
				print "No data to upload: " + str(new_data)
			return
		#the data is sent in the JSON format as the body of the request
		payload = json.dumps(new_data)
		print "payload " + str(payload)
		
		url = self.HYDROSERVER_URL + 'values'
		req = urllib2.Request(url)
		req.add_header('Content-Type', 'application/json')
		if self.no_upload:
			print "No Upload option set, data will not be uploaded"
		else:
			#upload the data to the web and check for any error status codes
			try:
				response = urllib2.urlopen(req, payload)
				status = json.load(response)
				print status
			except urllib2.HTTPError, e:
				print e.code
				print e.msg
				print e.headers
				print e.fp.read()

	#this script reads the lookup-table and for each row, gets the logger-port-response-site-variable-method information
	#this should include the SiteCode, SiteID, VariableID, MethodID
	###################################################################
	# Uploads the data for all sites from the sensor.				  #
	###################################################################
	def upload_data(self, sensor_name):
		#get the sensor metadata:
		#sensor, response, variable code, and method id
		sensor_metadata = self.get_sensor_metadata(sensor_name)
		
		#open the lookup table
		book = xlrd.open_workbook(self.xlsfile)
		sheets = book.sheets()
		sheet0 = sheets[0]
		nr = sheet0.nrows
		upload_file = "None"
		for i in range(1, nr):
			logger = sheet0.cell_value(i, 0)
			site_code = sheet0.cell_value(i, 1)
			port = int(sheet0.cell_value(i, 4))
			sensor = sheet0.cell_value(i, 5)

			#find the corresponding site ID
			site_id = self.get_site_id(site_code)
			if site_id is None:
				if self.verbose:
					print 'SiteID not found on server for SiteCode: ' + site_code
				continue
			
			#if automatically uploading, use dxd files
			if self.manual_upload_file == None:
				#find the right DXD file for the logger of this sensor
				upload_file = '%s%s.dxd' % (self.dxd_folder, logger)
				if not self.is_file(upload_file):
					continue
			else:
				upload_file = str(self.manual_upload_file)
				if str(logger) not in upload_file:
					continue
			if self.verbose:
				print "sensor metadata" + str( sensor_metadata)
			#start the uploading
			if sensor == sensor_name:
				for md in sensor_metadata:
					self.sensor_upload(site_id=site_id,
					  site_code=site_code,
					  variable_id=md["variable_id"],
					  method_id=md["method"],
					  source_id=1,
					  resp=md["response"],
					  upload_file=upload_file,
					  port=port,
					  sensor=sensor,
					  logger=logger)


def get_timestamp(updater, namespace):
	#this method either sets the timestamp based on one passed in by the user or 
	#loops through a set of 10 sites and variables, gets the latest dates from each from the database
	#and compares them to find the most recent to avoid uploading old values again. An argument can be passed
	#in to specify not to use dxd files, but to upload from xls files instead. 
	
	#uses optional arg as another date if present
	if namespace.latest_upload_time != None:
		old_time_str = namespace.latest_upload_time
		try:
			temp_timestamp = parse(old_time_str)
			updater.old_timestamp = temp_timestamp
			return
		except Exception:
			print "Timestamp given is invalid"

	 
	from suds.client import Client
	client = Client("http://worldwater.byu.edu/app/index.php/rushvalley/services/cuahsi_1_1.asmx?WSDL")
	#maps site IDs to variable codes
	sites_dict = { 
		'Ru2BNM5': 'GS3_Moisture_Temp',
		'Ru2BNMA': 'SRS_Nr_NDVI_sixthirty',
		'Ru4BNC5': 'GS3_Moisture_VWC',
		'Ru1BNC5': 'GS3_Moisture_EC',
		'Ru1BMNA': 'SRS_Nr_NDVI_eighthundred',
		'Ru1BNCA': 'SRS_Nr_NDVI',
		'Ru3BMMA': 'SRS_Nr_NDVI_eighthundred',
		'Ru5BMMA': 'SRS_Nr_NDVI',
		'Ru2BMPA': 'SRS_Nr_NDVI_sixthirty',
		'Ru5BMM5': 'GS3_Moisture_EC'
	}

	for site in sites_dict:
		variable = "rushvalley:" + sites_dict[site]
		site = "rushvalley:" + site
		obj = client.service.GetValuesObject(site, variable )
		try:
			inner_time = obj.timeSeries[0].values[0].value[-1]._dateTime
			if updater.verbose:
				print inner_time
			if updater.old_timestamp == "none":
				updater.old_timestamp = inner_time
			elif inner_time > updater.old_timestamp:
				updater.old_timestamp = inner_time
		except Exception:
			print "Failed to get timestamp from database for site " + site + " and variable " + variable

	

if __name__ == '__main__':

	parser = argparse.ArgumentParser(description = "Downloads data from Decagon server in .dxd files.\n" +
		"Optionally accepts a timestamp argument, which it uses to ignore old values already uploaded. " + 
		"Additionally, the optional xls argument causes script to upload from a local xls file instead " 
		"of a downloaded dxd file (for offline logger manual upload).")
	parser.add_argument("-lt", "--latest_upload_time", help="String of latest upload time. Ex. '2015-06-15 00:00:00'")
	parser.add_argument("-xls", "--xls_file", help="Name of xls file to use instead of .dxd files, for manual upload.",
	type=argparse.FileType('r'))
	parser.add_argument("-v", "--verbose", action='store_true', help="Print out messages while running")
	parser.add_argument("-nu", "--no_upload", action='store_true', help="Don't upload data, used for testing")
	
	namespace = parser.parse_args()

	#If xls file passed in, dxd files not used
	if namespace.xls_file == None:
		#STEP 1: Get the data from DECAGON data loggers
		decagon.download_all('passwords.csv','dxd')

	#STEP 2: Upload the data to HydroServer
	u = Updater()
	u.verbose = namespace.verbose
	u.no_upload = namespace.no_upload
	get_timestamp(u, namespace)
	u.manual_upload_file = namespace.xls_file;

	u.dxd_folder = 'dxd/'
	u.upload_data('SRS')
	u.upload_data('PYR')
	u.upload_data('MPS-6')
	u.upload_data('GS3')

	if u.manual_upload_file != None:
		u.upload_data('5TE')
		u.upload_data('5TM')
