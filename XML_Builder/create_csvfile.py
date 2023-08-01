import os
import path
import csv  
from config import *


#=============================================== CSV file for tool result =================================
def save(filename, records):
	with open(filename, 'w+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = tool_csv_header)
		writer.writeheader()
		for record in records:
			writer.writerow(record)

def build_tree(filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = tool_csv_header)
		writer.writeheader()


#========================================= CSV file for ground-truth result =================================
def gt_save(filename, records):
	with open(filename, 'w+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = gt_header)
		writer.writeheader()
		for record in records:
			writer.writerow(record)

def gt_generate(filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = gt_header)
		writer.writeheader()


#========================================= CSV file for app records =================================

def app_save(filename, records):
	with open(filename, 'w+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = apps_header)
		writer.writeheader()
		for record in records:
			writer.writerow(record)

def app_build_tree(filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = apps_header)
		writer.writeheader()


#========================================= CSV file for final result =================================

def result_save(filename, records):
	with open(filename, 'w+') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = all_app_results)
		writer.writeheader()
		for record in records:
			writer.writerow(record)

def result_build_tree(filename):
	with open(filename, 'w') as csvfile:
		writer = csv.DictWriter(csvfile, fieldnames = all_app_results)
		writer.writeheader()
