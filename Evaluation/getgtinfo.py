from config import *
import xml.etree.ElementTree as ET
import glob
import os
import pathlib
import pandas as pd
from itertools import chain




def get_image_change_info(node):
	for child_node in node.iter('node'):
		node_type = child_node.attrib.get('node-type')
		if(node_type == 'old-component'):
			node_attributes = child_node.find('node').attrib

		if(node_type == 'new-component'):
			new_attributes = child_node.find('node').attrib
	old_bounds = node_attributes['bounds'].replace(" ","")
	new_bounds = new_attributes['bounds'].replace(" ","")
	change_category = []
	change_category.append('IC')
	info = {}
	info['old_bounds'] = old_bounds
	info['new_bounds'] = new_bounds
	info['node_attributes'] = node_attributes
	info['new_attributes'] = new_attributes
	info['change_types'] = change_category
	info['class'] = new_attributes['class'].split(".")[-1]
	#print(info)
	return info




def get_removed_component_info(node):
	node_attributes = node.find('node').find('node').attrib
	old_bounds = node_attributes['bounds'].replace(" ","")
	change_category = []
	change_category.append('CR')
	info = {}
	info['old_bounds'] = old_bounds
	info['new_bounds'] = None
	info['node_attributes'] = node_attributes
	info['new_attributes'] = None
	info['change_types'] = change_category
	info['class'] = node_attributes['class'].split(".")[-1]
	#print(info)
	return info




def get_color_change_info(node):
	for child_node in node.iter('node'):
		node_type = child_node.attrib.get('node-type')
		if(node_type == 'old-component'):
			node_attributes = child_node.find('node').attrib

		if(node_type == 'new-component'):
			new_attributes = child_node.find('node').attrib
	component_type = node_attributes['class'].split(".")[-1]
	old_bounds = node_attributes['bounds'].replace(" ","")
	new_bounds = new_attributes['bounds'].replace(" ","")
	change_category = []
	change_category.append('CC')
	info = {}
	info['old_bounds'] = old_bounds
	info['new_bounds'] = new_bounds
	info['node_attributes'] = node_attributes
	info['new_attributes'] = new_attributes
	info['change_types'] = change_category
	info['class'] = new_attributes['class'].split(".")[-1]
	#print(info)
	return info




def get_text_change_info(node):
	change_category = []
	old_text = node.attrib.get('old-text')
	new_text = node.attrib.get('new-text')
	change_category.append('TC')
	
	for child_node in node.iter('node'):
		node_type = child_node.attrib.get('node-type')
		if(node_type == 'old-component'):
			node_attributes = child_node.find('node').attrib
		if(node_type == 'new-component'):
			new_attributes = child_node.find('node').attrib

	old_bounds = node_attributes['bounds'].replace(" ","")
	new_bounds = new_attributes['bounds'].replace(" ","")
	
	info = {}
	info['old_bounds'] = old_bounds
	info['new_bounds'] = new_bounds
	info['node_attributes'] = node_attributes
	info['new_attributes'] = new_attributes
	info['change_types'] = change_category
	info['class'] = new_attributes['class'].split(".")[-1]
	#print(info)
	return info




def get_added_component_info(node):
	new_attributes = node.find('node').find('node').attrib
	new_bounds = new_attributes['bounds'].replace(" ","")
	change_category = []
	change_category.append('CA')
	info = {}
	info['old_bounds'] = None
	info['new_bounds'] = new_bounds
	info['node_attributes'] = None
	info['new_attributes'] = new_attributes
	info['change_types'] = change_category
	info['class'] = new_attributes['class'].split(".")[-1]
	#print(info)
	return info



#get the information on changes in component location, size or color. This excludes text color.
def get_location_size_color_text_change_info(node, change_type):
	old_bounds = ""
	new_bounds = ""
	change_category = []
	info = {}
	
	if change_type == 'text-color-change':
		change_category.append('TXC')
		for child_node in node.iter('node'):
			node_type = child_node.attrib.get('node-type')
			if(node_type == 'old-component'):
				node_attributes = child_node.find('node').attrib
			if(node_type == 'new-component'):
				new_attributes = child_node.find('node').attrib
		old_bounds = node_attributes['bounds'].replace(" ","")
		new_bounds = new_attributes['bounds'].replace(" ","")
		info['old_bounds'] = old_bounds
		info['new_bounds'] = new_bounds
	
	else:
		if 'old-location-text' in node.attrib.keys():
			old_location_text = node.attrib.get('old-location-text')
			new_location_text = node.attrib.get('new-location-text')
			old_bounds = old_location_text.split("-")[0].replace(" ","")
			new_bounds = new_location_text.split("-")[0].replace(" ","")
			old_text = old_location_text.split("-")[1]
			new_text = new_location_text.split("-")[1]
			if old_text != new_text:
				change_category.append('TC')
		if 'old-color-size' in node.attrib.keys():
			old_color_size = node.attrib.get('old-color-size')
			new_color_size = node.attrib.get('new-color-size')
			old_color = old_color_size.split("-")[0]
			new_color = new_color_size.split("-")[0]
			old_bounds = old_color_size.split("-")[1].replace(" ","")
			new_bounds = new_color_size.split("-")[1].replace(" ","")
			if old_color != new_color:
				change_category.append('CC')
		if 'old-location' in node.attrib.keys():
			old_bounds = node.attrib.get('old-location').replace(" ","")
			new_bounds = node.attrib.get('new-location').replace(" ","")
		if 'old-size' in node.attrib.keys():
			old_bounds = node.attrib.get('old-size').replace(" ","")
			new_bounds = node.attrib.get('new-size').replace(" ","")
		old_x = old_bounds.split(",")[0]
		old_y = old_bounds.split(",")[1]
		old_w = old_bounds.split(",")[2]
		old_h = old_bounds.split(",")[3]
		new_x = new_bounds.split(",")[0]
		new_y = new_bounds.split(",")[1]
		new_w = new_bounds.split(",")[2]
		new_h = new_bounds.split(",")[3]
		if old_x!=new_x:
			change_category.append('HT')
		if old_y!=new_y:
			change_category.append('VT')
		if old_w!=new_w:
			change_category.append('HS')
		if old_h!=new_h:
			change_category.append('VS')
	
		info['old_bounds'] = '['+str(old_x)+','+str(old_y)+']['+str(old_w)+','+str(old_h)+']'
		info['new_bounds'] = '['+str(new_x)+','+str(new_y)+']['+str(new_w)+','+str(new_h)+']'
	
	for child_node in node.iter('node'):
		node_type = child_node.attrib.get('node-type')
		if(node_type == 'old-component'):
			node_attributes = child_node.find('node').attrib

		if(node_type == 'new-component'):
			new_attributes = child_node.find('node').attrib

	info['node_attributes'] = node_attributes
	info['new_attributes'] = new_attributes
	info['change_types'] = change_category
	info['class'] = new_attributes['class'].split(".")[-1]

	return info





def extract_info(gt_xml):
	location_size_color_change_info = None
	added_component_info = None
	text_change_info = None
	color_change_info = None
	removed_component_info = None
	image_change_info = None

	tree = ET.parse(gt_xml)
	root = tree.getroot()
	combined_info = []
	for node in root.iter('node'):
		change_type = node.attrib.get('change-type')
		if change_type == 'component-location' or change_type == 'text-color-change' or change_type == 'image-location-change' or change_type == 'component-size' or change_type == 'color-size-change' or change_type == 'location-text-change':
			combined_info.append(get_location_size_color_text_change_info(node, change_type))
			#print(change_type)
		if change_type == 'component-add':
			combined_info.append(get_added_component_info(node))
			#print(change_type)
		if change_type == 'text-change':
			#print(get_text_change_info(node))
			combined_info.append(get_text_change_info(node))
			#print(change_type)
		if change_type == 'color-change' or change_type == 'two-color-change' or change_type == 'multi-color-change':
			combined_info.append(get_color_change_info(node))
			#print(change_type)
		if change_type == 'component-remove':
			combined_info.append(get_removed_component_info(node))
			#print(change_type)
		if change_type == 'image-change':
			combined_info.append(get_image_change_info(node))
			#print(change_type)
	return combined_info
		