from config import *
from skimage.metrics import structural_similarity as ssim
import cv2
import os
import numpy as np
import imutils
import copy
import pandas as pd


def isWithinBoundary(x, y, w, h):
	if x>=0 and y>=63 and x+w <= 1080 and h <= 1857:
	    return True
	else:
		False
			

def locate_old_component(template, image, call_originator):
	gray_template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
	canny_gray_template = cv2.Canny(gray_template, 100,200, apertureSize=3)
	(tH, tW) = canny_gray_template.shape[:2]
	gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
	found = None
	for scale in np.linspace(0.2, 2.0, 10)[::-1]:
		resized = imutils.resize(gray, width = int(gray.shape[1]*scale), height = int(gray.shape[0]*scale))
		if resized.shape[0] < tH or resized.shape[1] < tW:
			break
		r = gray.shape[1]/float(resized.shape[1])
		edged = cv2.Canny(resized, 100, 200, apertureSize=3)
		result = cv2.matchTemplate(edged, canny_gray_template, cv2.TM_CCOEFF)
		(_,maxVal,_,maxLoc) = cv2.minMaxLoc(result)
		if found is None or maxVal > found[0]:
			found = (maxVal, maxLoc, r)
	(_,maxLoc,r) = found
	(startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))	
	(endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
	cropped_component = image[startY:endY, startX:endX]
	gray_cropped_component = cv2.cvtColor(cropped_component, cv2.COLOR_BGR2GRAY)

	#resizing the cropped component to match the shape with that of the template
	(H, W) = gray_template.shape
	if H < 7:
		H = 7
	if W < 7:
		W = 7
	gray_template = cv2.resize(gray_template, (W, H))
	(H, W) = gray_template.shape
	gray_cropped_component = cv2.resize(gray_cropped_component, (W, H))
	(H, W, C) = template.shape
	if H < 7:
		H = 7
	if W < 7:
		W = 7
	template = cv2.resize(template, (W, H))
	(H, W, C) = template.shape
	cropped_component = cv2.resize(cropped_component, (W, H))
	sim_gray = ssim(gray_template,gray_cropped_component,full=True)[0]
	sim_rgb = ssim(template,cropped_component,full=True,channel_axis=2)[0]
	#sim = 1 means that the component has been found in the mockup GUI
	
	x = None
	y = None 
	w = None
	h = None
	locator_flag = False
	color_changed_flag = False

	if sim_gray != sim_rgb:
		color_changed_flag = True
	if sim_gray > 0.96: 
		locator_flag = True
		x = startX
		y = startY
		w = endX-x
		h = endY-y	

	if call_originator == "lcd_leaf" or call_originator == "rcd_old":
		return locator_flag, color_changed_flag, x, y, w, h
	if call_originator == "rcd_added" or call_originator == "lcd_parent":
		return startX, startY, endX, endY



def crop_old_component(root_directory, old_xml, old_png, new_png, component_boundary):
	oldGUI_components = {}
	oldGUI_directory = root_directory + dirs['old_comps']
	for i in component_boundary:
		x = int(component_boundary[i][0])
		y = int(component_boundary[i][1])
		w = int(component_boundary[i][2])
		h = int(component_boundary[i][3])
		component = old_png[y:h, x:w]
		oldGUI_components[i] = [x,y,w,h]
		if not os.path.exists(oldGUI_directory):
			os.makedirs(oldGUI_directory)
		#print(i, (x,y,w,h))
		cv2.imwrite(oldGUI_directory+"/old-"+str(i)+".png",component)
	return oldGUI_directory, oldGUI_components



#this function detects the gui components from the gui of old app version onto the gui mockup of the new app version
def get_record(root_directory, old_xml, old_png, new_png, info_dict, old_comp_boundaries):
	oldGUI_directory, oldGUI_components = crop_old_component(root_directory, old_xml, old_png, new_png, old_comp_boundaries)
	df = pd.read_csv(root_directory+csv_filename)
	
	for i in oldGUI_components:
		isParent = df.loc[i-1,"isParent"] == "Parent"
		isLeaf = df.loc[i-1,"isParent"] == "Leaf"
		if isParent:
			template = cv2.imread(oldGUI_directory+"/old-"+str(i)+'.png')
			new_x,new_y,new_w,new_h = locate_old_component(template, new_png, "lcd_parent")
			locator_flag = True
			color_changed_flag = False
		if isLeaf:
			template = cv2.imread(oldGUI_directory+"/old-"+str(i)+'.png')
			locator_flag,color_changed_flag,new_x,new_y,new_w,new_h = locate_old_component(template, new_png, "lcd_leaf")

		ct = [] #change_type
		cd = [] #change_desciption

		#if component was not located on the mockup gui
		if not locator_flag:
			tc = info_dict[i]['total_changes']
			updated_tc = tc+1
			ct.append('CR')
			cd.append('Component has been removed')
			info_dict[i].update({'total_changes': updated_tc})
			info_dict[i].update({'change_types': ct})
			info_dict[i].update({'change_description': cd})
			info_dict[i]['new_attributes'] = "NA"
			info_dict[i]['new_bounds'] = "NA"

		
		#if component has been located on the mockup gui
		if locator_flag:
			#then set the new bounds with the retreived coordinates
			new_bounds = '['+str(new_x)+','+str(new_y)+']['+str(new_w)+','+str(new_h)+']'
			#then update the dictionary
			info_dict[i].update({'new_bounds':new_bounds})
			#then update the node attributes
			temp = info_dict[i]['node_attributes']
			info_dict[i]['new_attributes'] = copy.deepcopy(info_dict[i]['node_attributes'])
			info_dict[i]['new_attributes'].update({'bounds':info_dict[i]['new_bounds']})

			#getting old boundaries
			old_x = oldGUI_components[i][0]
			old_y = oldGUI_components[i][1]
			old_w = oldGUI_components[i][2]
			old_h = oldGUI_components[i][3]


			#if component x position has been changed:
			if old_x != new_x:
				tc = info_dict[i]['total_changes']
				updated_tc = tc+1
				info_dict[i].update({'total_changes': updated_tc})
				ct.append('HT')
				cd.append('Component has been horizontally translated')
				info_dict[i].update({'change_types': ct})
				info_dict[i].update({'change_description': cd})	

			#if component y position has been changed:
			if old_y != new_y:
				tc = info_dict[i]['total_changes']
				updated_tc = tc+1
				info_dict[i].update({'total_changes': updated_tc})
				ct.append('VT')
				cd.append('Component has been vertically translated')
				info_dict[i].update({'change_types': ct})
				info_dict[i].update({'change_description': cd})

			#if component height has been changed:
			if old_h != new_h:
				tc = info_dict[i]['total_changes']
				updated_tc = tc+1
				info_dict[i].update({'total_changes': updated_tc})
				ct.append('VS')
				cd.append('Component size has been changed vertically')
				info_dict[i].update({'change_types': ct})
				info_dict[i].update({'change_description': cd})

			#if component width has been changed:
			if old_w != new_w:
				tc = info_dict[i]['total_changes']
				updated_tc = tc+1
				info_dict[i].update({'total_changes': updated_tc})
				ct.append('HS')
				cd.append('Component size has been changed horizontally')
				info_dict[i].update({'change_types': ct})
				info_dict[i].update({'change_description': cd})
		
			#if component color has been changed:
			if color_changed_flag:
				tc = info_dict[i]['total_changes']
				updated_tc = tc+1
				info_dict[i].update({'total_changes': updated_tc})
				ct.append('CC')
				cd.append('Component color has been changed')
				info_dict[i].update({'change_types': ct})
				info_dict[i].update({'change_description': cd})
	
	records = []
	for i in range(1,len(info_dict)+1):
		records.append(info_dict[i])
	return records


