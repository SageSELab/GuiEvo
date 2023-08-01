from config import *
import cv2
import numpy as np
import imutils
import os
import copy
import csv  
import Detection.layout as lcd
import Detection.text as text
import Detection.redrawClassifier as labeler
import pandas as pd
import itertools 
from collections import OrderedDict
from collections.abc import Iterable
import pytesseract
import re
from PIL import Image
from easyocr import Reader
import math

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'



#https://stackoverflow.com/questions/69692851/how-to-expand-list-in-list-that-included-in-some-not-iterable-objects-to-flat
def flatten(successors):
    if isinstance(successors, Iterable):
        return [a for i in successors for a in flatten(i)] # recursively calling
    else:
        return [successors]



def get_successor_list(parent_node_num, df, all_child_is_leaf):
	successors = []
	while not all_child_is_leaf:
		children = df.loc[df['parent_node_num'] == parent_node_num]['node_num'].tolist()
		for child in children:
			successors.append(child)
			if df.loc[df['node_num'] == child]['isParent'].values[0] == "Parent":
				#print(child,'is a parent too. Moving to its child(ren)')
				successors.append(get_successor_list(child, df, False))
				all_child_is_leaf = True
			else:
				#print(child,'is a leaf')
				all_child_is_leaf = True
	return successors	




def insert_added_component(added_component,df,root_directory):
	#setting up attributes for the added component
	added_component_bound = added_component['bounds']
	x = added_component_bound[0]
	y = added_component_bound[1]
	w = added_component_bound[2]
	h = added_component_bound[3]
	added_component_parent_node_num = added_component['parent_node_num']
	added_component_parent_location = df.loc[df['parent_node_num'] == added_component['parent_node_num']]['parent_location'].tolist()[0]
	added_component_level = df.loc[df['parent_node_num'] == added_component_parent_node_num]['xml_level'].tolist()[0]
	added_component_siblings_nodenums = df.loc[df['parent_node_num'] == added_component_parent_node_num]['node_num'].tolist()
	added_component_change_type = ['CA']
	added_component_change_description = ['Component has been added']
	total_siblings_of_added_component = len(added_component_siblings_nodenums)
	added_component_index = str(total_siblings_of_added_component)
	added_component_attribute = {}
	added_component_attribute['index'] = added_component_index
	added_component_attribute['text'] = added_component['text']
	added_component_attribute['resource-id'] = added_component['type']+'-'+str(added_component_index)
	added_component_attribute['class'] = 'android.widget.'+added_component['type']
	added_component_attribute['package'] = added_component['package']
	added_component_attribute['content-desc'] = ''
	added_component_attribute['checkable'] = ''
	added_component_attribute['checked'] = ''
	added_component_attribute['clickable'] = ''
	added_component_attribute['enabled'] = ''
	added_component_attribute['focusable'] = ''
	added_component_attribute['focused'] = ''
	added_component_attribute['scrollable'] = ''
	added_component_attribute['ong-clickable'] = ''
	added_component_attribute['password'] = ''
	added_component_attribute['selected'] = ''
	added_component_attribute['bounds'] = '['+str(x)+','+str(y)+']['+str(w)+','+str(h)+']'

	#adjusting node numbers and parent node number after adding the new component
	successors = flatten(get_successor_list(added_component_parent_node_num, df, False))
	last_successor_node = successors[-1]
	last_node_num_of_upper_split = last_successor_node
	first_node_num_of_lower_split = last_successor_node+1	
	split_index = first_node_num_of_lower_split-1
	df1 = df[:first_node_num_of_lower_split]
	df2 = df[first_node_num_of_lower_split:]
	new_node_num = split_index+1
	new_node = pd.DataFrame({'node_num': [new_node_num],'xml_level': [added_component_level],'xml_index': [added_component_index],'parent_location': [added_component_parent_location],'parent_node_num': [added_component_parent_node_num],'isParent' : ['Leaf'],'node_attributes' : None,'component_validity': None,'old_bounds': None,'new_bounds' : [added_component_attribute['bounds']],'total_changes': [1],'change_types': [added_component_change_type],'new_attributes': [added_component_attribute],'class':added_component['type']})
	#df.loc[new_node_num, 'new_bounds'] = added_component_attribute['bounds']

	df1 = df[:split_index]
	df2 = df[split_index:]
	
	if len(df2) == 0:
		df = pd.concat([df1, new_node], ignore_index = True, axis = 0)
	else:
		df = pd.concat([df1, new_node, df2], ignore_index = True, axis = 0)
		df_nodes = df['node_num'].tolist() 
		df2_nodes = df2['node_num'].tolist() 
		new_parent_nodes = {}
		for i in range(len(df2_nodes)):
			new_parent_nodes[df2_nodes[i]] = df2_nodes[i]+1
		for i in range(len(df_nodes)):
			if df.loc[i,'parent_node_num'] in new_parent_nodes.keys():
				df.loc[i,'parent_node_num'] = new_parent_nodes[df.loc[i,'parent_node_num']]
		for i in range(split_index+1,len(df_nodes)):
			df.loc[i,'node_num'] = df.loc[i,'node_num']+1

	return df



"""
def sort_comps_by_bbox(children_bbox):
	#https://stackoverflow.com/questions/38654302/how-can-i-sort-contours-from-left-to-right-and-top-to-bottom		
	keys = [key for key, value in children_bbox.items()]
	contours = [value for key, value in children_bbox.items()]
	formated_contours = {}
	for key in keys:
		bound = children_bbox[key]
		bound = bound.replace("][",",").replace("[","").replace("]","").strip().split(",")
		x = int(bound[0])
		y = int(bound[1])
		w = int(bound[2])
		h = int(bound[3])
		formated_contours[key] = (x,y,w,h)

	c = np.array(list(formated_contours.values()))
	max_height = np.max(c[::, 3])
	# Sort the formated_contours by y-value
	by_y = sorted(formated_contours.values(), key=lambda x: x[1])  # y values
	line_y = by_y[0][1]       # first y
	line = 1
	by_line = []
	# Assign a line number to each contour
	for x, y, w, h in by_y:
		if y > line_y + max_height:
			line_y = y
			line += 1        
		by_line.append((line, x, y, w, h))
	# This will now sort automatically by line then by x
	contours_sorted = [(x, y, w, h) for line, x, y, w, h in sorted(by_line)]
	sorted_child_nodes = []
	for contour in contours_sorted:
		sorted_child_nodes.append(list(children_bbox.keys())[list(children_bbox.values()).index('['+str(contour[0])+','+str(contour[1])+']['+str(contour[2])+','+str(contour[3])+']')])
	return sorted_child_nodes




def sort_leaf_components(new_df,root_directory):
	print(new_df.iloc[:,[0,1,2,3,4,5,9]])
	leaf_node_nums = new_df.loc[new_df['isParent'] == "Leaf"]['node_num'].tolist()
	#parent_node_nums = new_df.loc[new_df['isParent'] == "Parent"]['node_num'].tolist()
	parent_child_dict = get_node_wise_children_list(new_df)
	for parent in parent_child_dict.keys():
		children_node_nums = [value for value in parent_child_dict[parent] if value in leaf_node_nums] #list(set(parent_child_dict[parent]) & set(leaf_node_nums))
		unsorted_child_index = [new_df.index[new_df['node_num'] == child_node] for child_node in children_node_nums]
		children_bbox = {}
		if len(children_node_nums)!=0:
			for child_node in children_node_nums:
				children_bbox[child_node] = new_df.loc[new_df['node_num'] == child_node]['new_bounds'].tolist()[0]
			sorted_children_node_nums = sort_comps_by_bbox(children_bbox)
			sorted_child_index = [new_df.index[new_df['node_num'] == child_node] for child_node in sorted_children_node_nums]
			demo_df = new_df.copy(deep=True)
			rows_to_add = []
			for i,j in zip(sorted_child_index,unsorted_child_index):
				rows_to_add.append((demo_df.iloc[i.values[0]],demo_df.iloc[j.values[0]]['node_num'],demo_df.iloc[j.values[0]]['xml_index']))
			for i, j in zip(unsorted_child_index, range(len(rows_to_add))):
				demo_df.drop([i.values[0]], axis=0, inplace=True)
				demo_df.loc[i.values[0]] = rows_to_add[j][0]
				demo_df.loc[i.values[0],'node_num'] = rows_to_add[j][1]
				demo_df.loc[i.values[0],'xml_index'] = rows_to_add[j][2]
				
	#print(demo_df.iloc[:,[0,1,2,3,4,5,9]])
	return demo_df
"""



def get_level_index_pair(i,  new_df):
	parent_level_index = new_df.loc[i,'parent_location']
	parent_xml_level = int(parent_level_index.split(',')[0].replace('(',''))
	parent_xml_index = int(parent_level_index.split(',')[1].replace(')','').replace(' ','').strip("'"))
	#parent_level_index = int(parent_xml_index)
	pair = (parent_xml_level,parent_xml_index)
	return pair




def get_leafmost_parent_bound(eligible_parents,new_df):
	parent_of_leaf_nodes = []
	node_nums = new_df['node_num']
	for i in range(len(new_df)):
		if i in node_nums and new_df.loc[i,'isParent'] == "Leaf":
			pair = get_level_index_pair(i, new_df)
			parent_of_leaf_nodes.append(pair)
	for i in range(len(parent_of_leaf_nodes)):
		for j in range(len(new_df)):
			if j in node_nums and new_df.loc[j,'xml_level'] == parent_of_leaf_nodes[i][0] and new_df.loc[j,'xml_index'] == parent_of_leaf_nodes[i][1]:
				return new_df.loc[j,'node_num'], new_df.loc[j,'new_bounds']



def find_leafmost_parent(added_component_bound,parent_bounds,new_df):
	eligible_parents = []
	for par_bound in parent_bounds:
		if par_bound[0] < added_component_bound[0] and par_bound[1] < added_component_bound[1]:
		    # If bottom-right inner box corner is inside the parent bounding box
			if added_component_bound[0] + added_component_bound[2] < par_bound[0] + par_bound[2] \
				and added_component_bound[1] + added_component_bound[3] < par_bound[1] + par_bound[3]:
				inclusion = "full"
				eligible_parents.append(par_bound)
			else:
				inclusion = "partial"
				eligible_parents.append(par_bound)
	node_num, node_bound =  get_leafmost_parent_bound(eligible_parents,new_df)
	#print(leaf_most_parent_bound)
	return node_num, node_bound



def get_parent_node_bounds(new_df):
	#print(df.iloc[:,[0,1,2,4,8]])
	parent_bounds = []
	node_nums = new_df['node_num']
	for i in range(len(new_df)):
		if i in node_nums and new_df.loc[i,'isParent'] == "Parent":
			bound = new_df.loc[i,'new_bounds']
			bound = bound.replace("][",",").replace("[","").replace("]","").strip().split(",")
			x = int(bound[0])
			y = int(bound[1])
			w = int(bound[2])
			h = int(bound[3])
			bound = (x,y,w,h)
			parent_bounds.append(bound)
	return parent_bounds



def update_parent_locations(new_df):
	node_nums = new_df['node_num']
	for i in range(len(new_df)):
		parent_location = ""
		if i == 0:
			parent_location = None
		elif i in node_nums:
			parent_node = new_df.loc[i,'parent_node_num']
			for j in range(len(new_df)):
				if j in node_nums and parent_node == new_df.loc[j,'node_num']:
					parent_xml_level = new_df.loc[j,'xml_level']
					parent_xml_index = new_df.loc[j,'xml_index']
					parent_location = "("+str(int(parent_xml_level))+", '"+str(int(parent_xml_index))+"')"
			new_df.loc[i,'parent_location'] = parent_location
	return new_df



def update_sibling_index_level(new_df, node_siblings,dn_parent_node_num):
	for i in range(len(node_siblings)):
		for j in range(len(new_df)):
			if new_df.loc[j,'node_num'] == node_siblings[i]:
				new_df.loc[j,'xml_index'] = str(i)
				new_df.loc[j,'parent_node_num'] = dn_parent_node_num
	return new_df




def get_child_node_siblings(dn, child_node_nums, new_df, child_info, current_node_nums):
	child_node_siblings = []
	for child_node_num in child_node_nums:
		#subsubcase-1.2.1: if it's child is not in the current list of node_nums it means it is also deleted, do nothing
		if child_node_num not in current_node_nums: 
			todo = None

		#subsubcase-1.2.2: if child is in the current list of node_nums
		else:
			for i in range(len(new_df)):
				if new_df.loc[i,'node_num'] == child_node_num:
					new_df.loc[i,'xml_level'] = child_info[child_node_num][2] #set to parents level
					#update index values based on siblings
					parent_child_dict = get_node_wise_children_list(new_df)
					siblings = get_siblings(child_node_num, parent_child_dict)
					child_node_siblings.append(siblings)
	child_node_siblings = [item for sublist in child_node_siblings for item in sublist]
	child_node_siblings = list(dict.fromkeys(child_node_siblings))
	child_node_siblings.sort()
	return child_node_siblings




def update_for_one_child_no_siblings(old_parent_child_dict, dn, current_node_nums, new_df, child_info):
	child_node_num = old_parent_child_dict[dn][0]
	#subsubcase-1.1.1: if it's child is not in the current list of node_nums which means it is also deleted
	if child_node_num not in current_node_nums: 
		return new_df
	#subsubcase-1.1.2: if child is in the current list of node_nums
	else:
		for i in range(len(new_df)):
			if new_df.loc[i,'node_num'] == child_node_num:
				new_df.loc[i,'xml_level'] = child_info[child_node_num][2] #set to parents level
				return new_df

	




def get_child_info(children_node_nums_list, df):
	child_info = {}
	for i in range(1,len(df)):
		node_num = df.loc[i,'node_num']
		if node_num in children_node_nums_list:
			child_info[node_num] = []
			child_level = df.loc[i,'xml_level']
			child_index = df.loc[i,'xml_index']
			parent_location = df.loc[i,'parent_location']
			parent_level = parent_location.split(',')[0].replace('(','') 
			parent_index = parent_location.split(',')[1].replace(')','').replace(' ','').strip("'") 
			child_tuple = (child_level, child_index, parent_level, parent_index)
			child_info[node_num] = child_tuple
			#print('Child node_num: '+str(node_num)+' Child node_level: '+str(child_level)+' Child node_index: '+str(child_index)+' Parent node_level: '+str(parent_level)+' Parent node_index: '+str(parent_index))
	return child_info




def get_siblings_info(siblings, df):
	sibling_info = {}
	for i in range(1,len(df)):
		node_num = df.loc[i,'node_num']
		if node_num in siblings:
			sibling_info[node_num] = []
			sibling_level = df.loc[i,'xml_level']
			sibling_index = df.loc[i,'xml_index']
			parent_location = df.loc[i,'parent_location']
			parent_level = parent_location.split(',')[0].replace('(','') 
			parent_index = parent_location.split(',')[1].replace(')','').replace(' ','').strip("'") 
			sibling_tuple = (sibling_level, sibling_index, parent_level, parent_index)
			sibling_info[node_num] = sibling_tuple
	return sibling_info




def get_siblings(node_num, parent_child_dict):
	for parent in parent_child_dict.keys():
		if node_num in parent_child_dict[parent]:
			total_child = len(parent_child_dict[parent])
			if total_child > 1:
				parent_child_dict[parent].remove(node_num)
				return parent_child_dict[parent]
			elif total_child == 1:
				return 0



def get_node_wise_children_list(df):
	parent_list = df['parent_node_num'].tolist()
	parent_list = list(dict.fromkeys(parent_list))
	parent_child_dict = {}
	for parent in parent_list:
		parent_child_dict[parent] = []
		for i in range(len(df)):
			node_num = df.loc[i,'node_num']
			if df.loc[i,'parent_node_num'] == parent:
				parent_child_dict[parent].append(node_num)
	return parent_child_dict			
				



def update_df_after_node_removal(new_df, root_directory,tv):
	original_df = pd.read_csv(root_directory+"/["+str(tv)+"]_basic_info.csv")
	old_node_nums = original_df['node_num'].tolist()
	old_parent_list = original_df['parent_node_num'].tolist()
	current_node_nums = new_df['node_num'].tolist()
	current_parent_list = new_df['parent_node_num'].tolist()
	old_parent_child_dict = get_node_wise_children_list(original_df)
	deleted_node_nums = []
	
	for i in range(len(old_node_nums)):
		if old_node_nums[i] not in current_node_nums:
			deleted_node_nums.append(old_node_nums[i])
	#looping over all deleted nodes to update the dataframe for the remaining nodes
	#updates will be done for the siblings and children of each deleted node
	for dn in deleted_node_nums:
		for i in range(len(original_df)):
			if original_df.loc[i,'node_num'] == dn:
				dn_index = original_df.loc[i,'xml_index']
				dn_level = original_df.loc[i,'xml_level']
				dn_parent_node_num = original_df.loc[i,'parent_node_num']
				dn_parent_location = original_df.loc[i,'parent_location']
		#check if the deleted node had any siblings or not
		parent_child_dict = copy.deepcopy(old_parent_child_dict)
		siblings = get_siblings(dn, parent_child_dict)
		if siblings != 0 and siblings!= None:
			for sibling in siblings:
				if sibling not in current_node_nums:
					absentSibling = True
				else:
					absentSibling = False
			#returned value contains (sibling_node_num, sibling_level, sibling_index)
			if not absentSibling:
				sibling_info = get_siblings_info(siblings, original_df)
		#check if the deleted node had any child or not
		if dn in old_parent_list:
			total_child = len(old_parent_child_dict[dn])
			#returned value contains (child_node_num, child_level, child_index, parent_level, parent_index)
			child_info = get_child_info(old_parent_child_dict[dn], original_df)
		else:
			total_child = 0

		#case-1: if the deleted node had children but no siblings
		if total_child != 0 and siblings == 0: 
			#subcase-1.1: if deleted node had only one child
			if total_child == 1:
				new_df = update_for_one_child_no_siblings(old_parent_child_dict, dn, current_node_nums, new_df, child_info)
			#subcase-1.2: if deleted node had more than one children
			else:
				child_node_nums = old_parent_child_dict[dn]
				#looping over all the children
				child_node_siblings = get_child_node_siblings(dn, child_node_nums, new_df, child_info, current_node_nums)
				new_df = update_sibling_index_level(new_df, child_node_siblings,dn_parent_node_num)
			child_node_nums = old_parent_child_dict[dn]
			for i in range(len(new_df)):
				if new_df.loc[i,'node_num'] in child_node_nums:
					new_df.loc[i,'xml_level'] = dn_level
					new_df.loc[i,'parent_node_num'] = dn_parent_node_num	
					new_df.loc[i,'parent_location'] = dn_parent_location
				else:
					todo = None	

		#case-2: if the deleted node had children and siblings too
		elif total_child != 0 and siblings != 0 and siblings!= None:
			for parent in old_parent_child_dict.keys():
				if dn_parent_node_num == parent:
					all_sibling_nodes = old_parent_child_dict[parent]
			for parent in old_parent_child_dict.keys():
				if dn == parent:
					all_child_nodes = old_parent_child_dict[parent]
			for child_node_num in all_child_nodes:
				if child_node_num not in current_node_nums:
					all_child_nodes.remove(child_node_num)
			list1 = []
			list2 = []
			for i in range(len(all_sibling_nodes)):
				if all_sibling_nodes[i] == dn:
					list1 = all_sibling_nodes[:i]
					list2 = all_sibling_nodes[i+1:]
			if len(all_child_nodes)!=0:
				all_nodes = list1 + all_child_nodes + list2
			else: 
				all_nodes = copy.deepcopy(all_sibling_nodes)	
			node_nums = new_df['node_num']
			if len(all_nodes) != 0:
				all_sibling_indices = {}
				for i in range(len(all_nodes)):
					all_sibling_indices[all_nodes[i]] = i
				for i in range(len(new_df)):
					if i in node_nums and new_df.loc[i,'node_num'] in all_nodes:
						node_num = new_df.loc[i,'node_num']
						new_df.loc[i,'xml_index'] = all_sibling_indices[node_num]	
						new_df.loc[i,'xml_level'] = dn_level
						new_df.loc[i,'parent_node_num'] = dn_parent_node_num	
						new_df.loc[i,'parent_location'] = dn_parent_location			

		#case-3: if the deleted node was a leaf node with siblings
		elif total_child == 0 and siblings != 0 and siblings!= None:
			all_sibling_indices = {}
			for i in range(len(siblings)):
				all_sibling_indices[siblings[i]] = i
			node_nums = new_df['node_num']
			for i in range(len(new_df)):
				if i in node_nums and new_df.loc[i,'node_num'] in siblings:
					node_num = new_df.loc[i,'node_num']
					new_df.loc[i,'xml_index'] = all_sibling_indices[node_num]	
			
		#case-4: if the deleted node was a leaf node and had no siblings
		elif total_child == 0 and (siblings == 0 or siblings == None):
			todo = None
	new_df = update_parent_locations(new_df)
	return new_df




def delete_removed_components(df,root_directory):
	new_df = df.copy(deep=True)
	#print(new_df.iloc[:, [0,1,2,3,10]])
	new_df = new_df[new_df['change_types'] != "['CR']"]
	#print(new_df.iloc[:, [0,1,2,3,10]])
	return new_df




def is_template_in_image(img, templ):
    result = cv2.matchTemplate(img, templ, cv2.TM_SQDIFF)
    min_val = cv2.minMaxLoc(result)[0]
    thr = 10e-6
    return min_val <= thr




def has_image(image, template, threshold):
	image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
	w, h = template.shape[::-1]
	res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
	loc = np.where(res >= threshold)
	try:
		assert loc[0][0] > 0
		assert loc[1][0] > 0
		return (loc[1][0], loc[0][0])
	except:
		return (-1, -1)




def get_contours(old_screen,new_screen):
	diff = old_screen.copy()
	
	old_im = Image.fromarray(old_screen)
	new_im = Image.fromarray(new_screen)
	if old_im.size != new_im.size:
		old_im = old_im.resize(new_im.size)   
		old_screen = np.asarray(old_im)
		diff = old_screen.copy()

	cv2.absdiff(old_screen, new_screen, diff)
	gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	kernel = np.ones((7,7), 'uint8')
	for i in range(0, 3):
		dilated = cv2.dilate(gray.copy(), kernel, iterations= i+1)
	(T, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
	cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	return cnts



def set_bounds(cnts, old_screen, new_screen, diffGUI_directory,tv):
	bounds = {}
	count = 1
	im = new_screen.copy()
	for c in cnts:
	# nicely fiting a bounding box to the contour
		(x, y, w, h) = cv2.boundingRect(c)
		crop_img = new_screen[y:y+h, x:x+w]
		crop_img_gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
		crop_img_gray_canny = cv2.Canny(crop_img_gray, 100,200, apertureSize=3)

		old_screen_gray = cv2.cvtColor(old_screen, cv2.COLOR_BGR2GRAY)
		old_screen_gray_canny = cv2.Canny(old_screen_gray, 100,200, apertureSize=3)

		if not is_template_in_image(old_screen_gray_canny,crop_img_gray_canny):
			bounds[count] = '['+str(x)+','+str(y)+']['+str(w)+','+str(h)+']'	
		cv2.imwrite(diffGUI_directory+"/["+str(tv)+"]_diff-"+str(count)+".png",crop_img)
		cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 3)
		count += 1
	return bounds


def check_for_old_components_within_new_bounds(added_comp_x,added_comp_y,added_comp_w,added_comp_h,new_df,added_component_filename):
	indices = []
	rows = new_df['change_types']
	for index,value in rows.iteritems():
		if not pd.isnull(value) and value != "['CR']":
			indices.append(index)
	for i in indices:
		pattern = re.escape('text') + r"(.*?)" + re.escape('resource-id')
		match = re.search(pattern, new_df.loc[i,'new_attributes'])
		old_text = match.group(1).strip().replace(": ","").replace(", ","").replace("'","")
		added_component_text = text.extract_text(cv2.imread(added_component_filename))
		substrings1 = set(old_text.split())
		substrings2 = set(added_component_text.split())
		common_substrings = substrings1.intersection(substrings2)
		if len(common_substrings) > 0 and old_text in added_component_text:
			added_component_text = added_component_text.replace(old_text,"")
			bound = new_df.loc[i,'new_bounds'].replace("][",",").replace("[","").replace("]","").strip().split(",")
			y = int(bound[1])
			h = int(bound[3])
			new_y = added_comp_y+h-y
			return (added_comp_x,new_y,added_comp_w,added_comp_h)
	return added_comp_x,added_comp_y,added_comp_w,added_comp_h


def extract_added_components(active_screen_bounds, diffGUI_directory, old_png, new_png, added_components,tv,new_df):
	for j in active_screen_bounds.keys():
		diff_comp = cv2.imread(diffGUI_directory+"/["+str(tv)+"]_diff-"+str(j)+".png")
		x, y = has_image(old_png, diff_comp, threshold = 0.70)
		if x >= 0 and y >= 0:
			todo = None
		else:
			added_component_filename = diffGUI_directory+"/["+str(tv)+"]_added-"+str(j)+".png"
			cv2.imwrite(added_component_filename,diff_comp)
			flag1,x,y,w,h = lcd.locate_old_component(diff_comp, new_png,j)
			added_comp_x,added_comp_y,added_comp_w,added_comp_h = check_for_old_components_within_new_bounds(x,y,w,h,new_df,added_component_filename)
			os.remove(diffGUI_directory+"/["+str(tv)+"]_added-"+str(j)+".png")
			os.remove(diffGUI_directory+"/["+str(tv)+"]_diff-"+str(j)+".png")
			crop_img = new_png[added_comp_y:added_comp_h, added_comp_x:added_comp_w]
			if crop_img is not None and np.any(crop_img != 0):
				cv2.imwrite(diffGUI_directory+"/["+str(tv)+"]_diff-"+str(j)+".png",crop_img)
				cv2.imwrite(diffGUI_directory+"/["+str(tv)+"]_added-"+str(j)+".png",crop_img)
				added_components[j] = {}
				added_components[j]['type'] = labeler.predict_label(added_component_filename)
				added_components[j]['bounds'] = (added_comp_x,added_comp_y,added_comp_w,added_comp_h)
	return added_components


def predict_new_activity_screen(new_png, old_activity_screen):
	f1, x,y,w,h = lcd.locate_old_component(old_activity_screen, new_png,0)
	predicted_bound =  new_png[y:h, x:w] #y,h,x,w
	#cv2.imshow("considered.png",predicted_bound)
	#cv2.waitKey(0)
	return predicted_bound


def get_activity_screens(old_png, new_png, info_dict):
	bound = info_dict[2]['old_bounds'] #x,y,w,h
	bound = bound.replace("][",",").replace("[","").replace("]","").strip().split(",")
	x = int(bound[0])
	y = int(bound[1])
	w = int(bound[2])
	h = int(bound[3])
	#screen height of 0:63 should be ignored
	if y <63:
		y = 63
	#cropping out the considerable region from the gui
	old_activity_screen =  old_png[y:h, x:w] #y,h,x,w
	if x == 0 and y == 63 and w == 1080 and h == 1794:
		new_activity_screen =  new_png[y:h, x:w] #y,h,x,w
	else:
		new_activity_screen = predict_new_activity_screen(new_png, old_activity_screen)
	return old_activity_screen, new_activity_screen



#this function detects added gui components using the screens from old and new version of the app
#component color changes and removed components have already been identified in layout_change_detector.py
def list_changes(dp,metadata_dir,info_dict,tv):
	root_directory = metadata_dir
	old_png, new_png = cv2.imread(dp[0]), cv2.imread(dp[2])
	active_screen_old_png, active_screen_new_png = get_activity_screens(old_png,new_png,info_dict)
	diffGUI_directory = root_directory+"/"+"diffGUI_directory"
	if not os.path.exists(diffGUI_directory):
		os.makedirs(diffGUI_directory)
	cnts = get_contours(active_screen_old_png,active_screen_new_png)
	active_screen_bounds = set_bounds(cnts, active_screen_old_png, active_screen_new_png, diffGUI_directory,tv)
	filename = root_directory +"/"+ '['+str(tv)+"]_basic_info.csv"
	df = pd.read_csv(filename)
	new_df = delete_removed_components(df,root_directory)
	new_df.to_csv(root_directory+"/"+'['+str(tv)+"]_info_with_cr.csv", index=False)
	new_df = update_df_after_node_removal(new_df, root_directory,tv)
	new_df.to_csv(root_directory+"/"+'['+str(tv)+"]_info_with_cr.csv", index=False)
	package_name = info_dict[2]['node_attributes']['package']
	#new_df = sort_leaf_components(new_df,root_directory)
	added_components = {}
	added_components = extract_added_components(active_screen_bounds, diffGUI_directory, old_png, new_png, added_components,tv,new_df)
	
	tc_rects = []
	indices = []
	rows = new_df['change_types']
	for index,value in rows.iteritems():
		if not pd.isnull(value):
			indices.append(index)
	
	for i in indices:
		bound = new_df.loc[i,'old_bounds'].replace("][",",").replace("[","").replace("]","").strip().split(",")
		x = int(bound[0]) 
		y = int(bound[1]) 
		w = int(bound[2]) 
		h = int(bound[3]) 

		x1 = x
		y1 = y 
		x2 = x + w
		y2 = y + h 
		tc_rect = (x1,y1,x2,y2)
		tc_rects.append(tc_rect)
		#print(bound)
	
	if len(added_components.keys())!=0:
		for i in added_components.keys():
			added_component_bound = added_components[i]['bounds']
			tc_rects.append(added_component_bound)
			#print("added:",added_component_bound)
	delet_key_list = []
	
	
	if len(added_components.keys())!=0:
		for tc_rect in tc_rects:
			for i in added_components.keys():
				added_component_bound = added_components[i]['bounds']
				x = added_component_bound[0]
				y = added_component_bound[1]
				w = added_component_bound[2]
				h = added_component_bound[3]
				x1 = x
				y1 = y
				x2 = x + w
				y2 = y + h
				addedcomp_rect = (x1,y1,x2,y2)
				"""
				Top-left corner: (x1, y1)
				Top-right corner: (x2, y1)
				Bottom-left corner: (x1, y2)
				Bottom-right corner: (x2, y2)
				"""
				if addedcomp_rect[0] > tc_rect[0] and addedcomp_rect[2] < tc_rect[2]:
					if addedcomp_rect[1] < tc_rect[1] and addedcomp_rect[3] > tc_rect[3]:
						if i not in delet_key_list:
							delet_key_list.append(i)

	indices = []
	new_texts = []
	rows = new_df['change_types']
	for index,value in rows.iteritems():
		if value == "['TC']":
			indices.append(index)
	
	for i in indices:
		pattern = re.escape('text') + r"(.*?)" + re.escape('resource-id')
		if new_df.loc[i,'isParent'] == 'Leaf':
			match = re.search(pattern, new_df.loc[i,'new_attributes'])
		if match:
			new_texts.append(match.group(1).strip())
		else:
			new_texts.append("")

	
	if len(added_components.keys())!=0:
		for i in added_components.keys():
			added_component_image = cv2.imread(diffGUI_directory+"/["+str(tv)+"]_added-"+str(i)+".png")
			added_component_image_text = text.extract_text(added_component_image)
			for texts in new_texts:
				if added_component_image_text in texts:
					delet_key_list.append(i)

	if len(delet_key_list)!=0:
		for key in delet_key_list:
			added_components.pop(key)
			os.remove(diffGUI_directory+"/["+str(tv)+"]_added-"+str(key)+".png")
			os.remove(diffGUI_directory+"/["+str(tv)+"]_diff-"+str(key)+".png")
	
	if len(added_components.keys())!=0:
		for i in added_components.keys():
			parent_node_bounds = get_parent_node_bounds(new_df)
			added_component_bound = added_components[i]['bounds']
			added_components[i]['package'] = package_name
			added_components[i]['parent_node_num'], added_components[i]['parent_node_bounds'] = find_leafmost_parent(added_component_bound,parent_node_bounds,new_df)
			added_components[i]['parent_type'] = info_dict[added_components[i]['parent_node_num']]['node_attributes']['class'].split(".")[-1]
			added_component_image = cv2.imread(diffGUI_directory+"/["+str(tv)+"]_added-"+str(i)+".png")
			added_components[i]['text'] = text.extract_text(added_component_image)
			if len(added_components[i]['text']) <= 1:
				added_components[i]['text'] = ""
			new_df = insert_added_component(added_components[i],new_df,root_directory)
			#new_df = sort_leaf_components(new_df,root_directory)
			#new_df = update_attributes(new_df,root_directory)
			#added_components[i]['xml_level'], added_components[i]['xml_index'], added_components[i]['node_num']
	new_df.to_csv(root_directory+"/"+'['+str(tv)+"]_dynamic_xml_base.csv", index=False)
			
