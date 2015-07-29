#! /usr/bin/env python
import sys
import os
import argparse

parser = argparse.ArgumentParser(description="Remove spaces from filenames.")
parser.add_argument("directory", help="directory containing the files to be renamed.")
parser.add_argument("-v", "--verbose", help="Output filenames while renaming.", action="store_true")
namespace = parser.parse_args()
directory = namespace.directory
if not os.path.isdir(directory):
	print "Error in directory argument. Rerun with -h option for help."
	sys.exit()

for root, dirs, files in os.walk(directory):
	for file_to_change in files:
		rel_path = root + "/" + file_to_change
		new_name = rel_path.replace(" ", "_")
		if namespace.verbose:
			print rel_path
			print new_name
			print
		os.rename(rel_path, new_name)
