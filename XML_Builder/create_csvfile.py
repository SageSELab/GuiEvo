import os
import path
import csv  
from config import *


header = [
	'node_num',
	'xml_level',
	'xml_index',
	'parent_location',
	'isParent',
	'node_attributes',
	'component_validity',
	'old_bounds',
	'new_bounds',
	'total_changes',
	'change_types',
	'change_description',
	'new_attributes'
	]


#this function will write component information to the csv file.
def save(filename, records):
	with open(filename, 'w+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = header)
		writer.writeheader()
		for record in records:
			writer.writerow(record)



def generate(filename):
	#The CSV file will contain the following information for all the components from old GUI and new GUI. 
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = header)
		writer.writeheader()