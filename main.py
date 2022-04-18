from config import *
import glob
import os
import pathlib
import cv2
import create_csvfile as csv_file
import xml_map
import boundary_retrieval as node_bounds
import layout_change_detector as lcd
import resource_change_detector as rcd
import create_dynxml as generatexml
import tag_parenthood



#this function generates the dynamic xml file for the mockup gui from the newer release of the app using the stored csv file
def form_dynamic_xml(stored_data, old_xml):
	generatexml.begin(stored_data, old_xml)
	print("Implementation complete")



#this function record the changes only for recurring components
#it also marks if any old component is not present in the new gui, which would help in tagging them as removed
#this function will record the following changes in a component: vertical/horizontal translation, vertical/horizontal size change 
def record_layout_change(root_directory, old_xml, old_png, new_png, info_dict, old_comp_boundaries):
	records = lcd.get_record(root_directory, old_xml, old_png, new_png, info_dict, old_comp_boundaries)
	return records



#this function will record the following: image color changes for recurring gui component(s), removed component(s), added component(s)
def	record_resource_change(root_directory, old_png, new_png, info_dict, old_comp_boundaries):
	rcd.list_added_components(root_directory, old_png, new_png, info_dict)
	records = None
	return records



#this function will record any changes in the text components
def	record_text_change(old_xml, old_png, new_png, info_dict, tree, old_comp_boundaries):
	
	records = None
	return records



def form_data_points(app_version_pairs):
	data_points = []
	files = []
	for version_pair in app_version_pairs:
		#for each of the version pair in the app, all existing files i.e. screenshot from the old version, 
		#mockup gui from the new version, and xml file of the old version are collected
		files.append([os.path.join(version_pair, fn) for fn in next(os.walk(version_pair))[2]])
	for input_files in files:
		old_png_path = list(filter(lambda x: "old_ss.png" in x, input_files))
		old_xml_path = list(filter(lambda x: "old_xml.xml" in x, input_files))
		new_png_path = list(filter(lambda x: "new_ss.png" in x, input_files))
		#each datapoint holds three input files: old gui, old xml, new mockup gui
		data_points.append((old_png_path, old_xml_path, new_png_path))
	return data_points



def get_app_version_pairs(apps):
	app_version_pairs = []
	for app in apps:
		for it in os.scandir(app):
			if it.is_dir():
				app_version_pairs.append(it.path)
	return app_version_pairs



def call_functions(old_xml, old_png, new_png, root_directory):
	#csv file is generated at first where all the recorded component changes will be stored
	#a dictionaty and xml tree (with parent-to-child mapping) is then formed using the xml file from older version of the app
	#Then component boundaries are retrieved and the dictionary is updated with the retrieved boundary information 
	
	csv_file.generate(root_directory+csv_filename)
	info_dict, tree = xml_map.parent_to_child(old_xml)
	info_dict, old_comp_boundaries, records = node_bounds.get_boundaries(info_dict, tree)
	csv_file.save(root_directory+csv_filename, records)
	tag_parenthood.get_parent_leaf_tag(root_directory)


	#layout changes are recorded and recorded layout changes are stored in the csv file
	layout_change_records = record_layout_change(root_directory, old_xml, old_png, new_png, info_dict, old_comp_boundaries)
	csv_file.save(root_directory+csv_filename, layout_change_records)
	tag_parenthood.get_parent_leaf_tag(root_directory)

	
	#resource changes are recorded and recorded layout changes are stored in the csv file
	resource_change_records = record_resource_change(root_directory, old_png, new_png, info_dict, old_comp_boundaries)
	#csv_file.save(root_directory+csv_filename, resource_change_records)
	#tag_parenthood.get_parent_leaf_tag(root_directory)

	"""
	#text changes are recorded
	text_change_records = record_text_change(old_xml, old_png, new_png, info_dict, tree, old_comp_boundaries)
	#recorded text changes are stored in the csv file
	csv_file.save(root_directory+csv_filename, text_change_records)
	
	
	#dynamic xml file is formed using the stored data in the csv file
	stored_data = root_directory+csv_filename
	form_dynamic_xml(stored_data, old_xml)
	"""


if __name__ == '__main__':
	root_directory = ""
	#sample dataset is chosen to detect changes
	if sample_dataset:
		#screenshot from older version of the app
		old_png = sample_data_directory + 'old.png'
		#xml file from older version of the app
		old_xml = sample_data_directory + 'old.xml'
		#mockup gui from newer version of the app
		new_png = sample_data_directory + 'new.png'
		#root of all the files
		root_directory = sample_data_directory
		#data point is pushed into the main implementation 
		call_functions(old_xml, cv2.imread(old_png), cv2.imread(new_png), root_directory)

	#evaluation dataset is chosen to detect changes
	if evaluation_dataset:
		apps = glob.glob(evaluation_data_directory+'*', recursive = True)
		app_version_pairs = get_app_version_pairs(apps)
		data_points = form_data_points(app_version_pairs)
		for data_point in data_points:
			#screenshot from older version of the app
			old_png = data_point[0][0]
			#xml file from older version of the app
			old_xml = data_point[1][0]
			#mockup gui from newer version of the app
			new_png = data_point[2][0]
			root_directory = new_png[:-10]
			#the data point is then pushed into the main implementation
			call_functions(old_xml, cv2.imread(old_png), cv2.imread(new_png), root_directory)
