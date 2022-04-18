from config import *
import cv2
import numpy as np
import imutils
import os
import copy
import csv  
import Layout_Change_Detection.layout_change_detector as lcd
import Resource_Change_Detection.redrawClassify as comp_label_detector
import pandas as pd
import itertools 


"""
def has_child(parent_location, df):
	child_nodes = []
	for i in range(len(df)):
		if df.loc[i,'parent_location'] == parent_location:
			child_nodes.append(df.loc[i,'node_num'])
	return child_nodes



def get_last_successor_node(parent_location, df):
	parent_nodes = df['parent_location']
	child_nodes = has_child(parent_location, df)
	i = 0
	for i in range (len(child_nodes)):
		node_num = child_nodes[i]
		if df.loc[node_num,'parent_location'] in parent_nodes:
			node_num = get_last_successor_node(parent_location, df)
"""			


def delete_removed_components(new_df):
	print(new_df.iloc[:, [0,1,2,10]])
	new_df = new_df[new_df['change_types'] != "['CR']"]
	print(new_df.iloc[:, [0,1,2,10]])
	return new_df





def create_component_location(added_component,df,root_directory):
	new_df = df.copy(deep=True)
	new_df = delete_removed_components(new_df)
	new_df.to_csv(root_directory+"gui_changes_with_applied_CR.csv", index=False)
	
	#children_list_of_parent = get_last_successor_node(parent_location, df)
	"""
	print(df.iloc[:, [0,1,2,3]])
	line = pd.DataFrame({"node_num": 100, "xml_level": 1, "xml_index": '3', "parent_location": "(8, '0')"}, index=[3])
	new_df = pd.concat([new_df.iloc[:2], line, new_df.iloc[2:]]).reset_index(drop=True)
	print(new_df.iloc[:, [0,1,2,3]])
	"""
	return None





def get_parent_level_index(eligible_parents,df):
	parent_of_leaf_nodes = []
	for i in range(len(df)):
		if df.loc[i,'isParent'] == "Leaf":
			parent_level_index = df.loc[i,'parent_location']
			parent_xml_level = int(parent_level_index.split(',')[0].replace('(',''))
			parent_xml_index = int(parent_level_index.split(',')[1].replace(')','').replace(' ','').strip("'"))
			parent_level_index = int(parent_xml_index)
			pair = (parent_xml_level,parent_xml_index)
			parent_of_leaf_nodes.append(pair)
	#print(parent_of_leaf_nodes)
	for i in range(len(parent_of_leaf_nodes)):
		for j in range(len(df)):
			if df.loc[j,'xml_level'] == parent_of_leaf_nodes[i][0] and df.loc[j,'xml_index'] == parent_of_leaf_nodes[i][1]:
				leaf_most_parent_bound = df.loc[j,'new_bounds']
				leaf_most_parent_bound = leaf_most_parent_bound.replace("][",",").replace("[","").replace("]","").strip().split(",")
				x = int(leaf_most_parent_bound[0])
				y = int(leaf_most_parent_bound[1])
				w = int(leaf_most_parent_bound[2])
				h = int(leaf_most_parent_bound[3])
				leaf_most_parent_bound = (x,y,w,h)
				if leaf_most_parent_bound in eligible_parents:
					return (df.loc[j,'xml_level'], str(df.loc[j,'xml_index']))
	




def find_leafmost_parent(added_component_bound,parent_bounds,df):
	eligible_parents = []
	for par_bound in parent_bounds:
		if par_bound[0] < added_component_bound[0] and par_bound[1] < added_component_bound[1]:
		    # If bottom-right inner box corner is inside the parent bounding box
			if added_component_bound[0] + added_component_bound[2] < par_bound[0] + par_bound[2] \
				and added_component_bound[1] + added_component_bound[3] < par_bound[1] + par_bound[3]:
				#print('The entire box is inside the parent bounding box: ',par_bound)
				eligible_parents.append(par_bound)
	leaf_most_parent_bound =  get_parent_level_index(eligible_parents,df)
	#print(leaf_most_parent_bound)
	return leaf_most_parent_bound





def get_parent_node_bounds(df):
	#print(df.iloc[:,[0,1,2,4,8]])
	parent_bounds = []
	for i in range(len(df)):
		if df.loc[i,'isParent'] == "Parent":
			bound = df.loc[i,'new_bounds']
			bound = bound.replace("][",",").replace("[","").replace("]","").strip().split(",")
			x = int(bound[0])
			y = int(bound[1])
			w = int(bound[2])
			h = int(bound[3])
			bound = (x,y,w,h)
			parent_bounds.append(bound)
	return parent_bounds




def predict_new_activity_screen(new_png, old_activity_screen):
	start_X,start_Y,end_X,end_Y = lcd.locate_old_component(old_activity_screen, new_png, "rcd_added")
	w = end_X - start_X
	h = end_Y - start_Y
	print(start_X, start_Y, w, h)
	predicted_bound =  new_png[start_Y:h, start_X:w] #y,h,x,w
	cv2.imshow("considered.png",predicted_bound)
	cv2.waitKey(0)
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
	new_activity_screen = predict_new_activity_screen(new_png, old_activity_screen)
	return old_activity_screen, new_activity_screen





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
	cv2.absdiff(old_screen, new_screen, diff)
	gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
	kernel = np.ones((7,7), 'uint8')
	for i in range(0, 3):
		dilated = cv2.dilate(gray.copy(), kernel, iterations= i+1)
	(T, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
	cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	return cnts




def set_bounds(cnts, old_screen, new_screen, diffGUI_directory):
	bounds = {}
	count = 1
	im = new_screen.copy()
	for c in cnts:
	# nicely fiting a bounding box to the contour
		(x, y, w, h) = cv2.boundingRect(c)
		crop_img = new_screen[y:y+h, x:x+w]
		if not is_template_in_image(old_screen,crop_img):
			bounds[count] = '['+str(x)+','+str(y)+']['+str(w)+','+str(h)+']'	
		cv2.imwrite(diffGUI_directory+"/diff-"+str(count)+".png",crop_img)
		cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 3)
		count += 1
	return bounds




def extract_added_components(active_screen_bounds, diffGUI_directory, old_png, new_png):
	added_components = {}
	for j in active_screen_bounds.keys():
		diff_comp = cv2.imread(diffGUI_directory+"/diff-"+str(j)+".png")
		x, y = has_image(old_png, diff_comp, threshold = 0.70)
		if x >= 0 and y >= 0:
			todo = None
		else:
			added_components[j] = {}
			added_component_filename = diffGUI_directory+"/added-"+str(j)+".png"
			cv2.imwrite(added_component_filename,diff_comp)
			flag1,flag2,x,y,w,h = lcd.locate_old_component(diff_comp, new_png, "rcd_old")
			added_components[j]['bounds'] = (x,y,w,h)
			added_components[j]['type'] = comp_label_detector.predict_label(added_component_filename)
	return added_components





#this function detects added gui components using the screens from old and new version of the app
#component color changes and removed components have already been identified in layout_change_detector.py
def list_added_components(root_directory, old_png, new_png, info_dict):
	active_screen_old_png, active_screen_new_png = get_activity_screens(old_png,new_png,info_dict)
	diffGUI_directory = root_directory+'/diffGUI_directory'
	if not os.path.exists(diffGUI_directory):
		os.makedirs(diffGUI_directory)
	cnts = get_contours(active_screen_old_png,active_screen_new_png)
	active_screen_bounds = set_bounds(cnts, active_screen_old_png, active_screen_new_png, diffGUI_directory)
	added_components = extract_added_components(active_screen_bounds, diffGUI_directory, old_png, new_png)
	for i in added_components.keys():
		df = pd.read_csv(root_directory+csv_filename)
		parent_node_bounds = get_parent_node_bounds(df)
		added_component_bound = added_components[i]['bounds']
		added_components[i]['parent_location'] = find_leafmost_parent(added_component_bound,parent_node_bounds,df)
		level, index, node_num = create_component_location(added_components[i],df,root_directory)
		#added_components[i]['xml_level'], added_components[i]['xml_index'], added_components[i]['node_num']

