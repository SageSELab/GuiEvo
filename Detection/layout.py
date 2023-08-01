from config import *
from skimage.metrics import structural_similarity as ssim
import cv2
import os
import numpy as np
import imutils
import copy
import pandas as pd
import Detection.resource as rcd
import re
import pytesseract
from PIL import Image
from easyocr import Reader
import Detection.text as text
import matplotlib.pyplot as plt


def check_for_color_changes(new_png, template, old_x, old_y, old_w, old_h, i):
	cropped_component = new_png[old_y:old_h, old_x:old_w]
	(height, width, C) = template.shape
	cropped_component = cv2.resize(cropped_component, (width, height))	
	mean_color1 = np.mean(template, axis=(0, 1))
	mean_color2 = np.mean(cropped_component, axis=(0, 1))
	color_diff = np.linalg.norm(mean_color1 - mean_color2)
	color_diff_threshold = 130.0
	is_color_change = color_diff > color_diff_threshold

	gray1 = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
	gray2 = cv2.cvtColor(cropped_component, cv2.COLOR_BGR2GRAY)
	canny_gray1 = cv2.Canny(gray1, 100,200, apertureSize=3)
	canny_gray2 = cv2.Canny(gray2, 100,200, apertureSize=3)
	ssim_score = ssim(canny_gray1, canny_gray2,channel_axis=None)
	return is_color_change, ssim_score
	

def update(tc, info_dict, i, ct, change_type):
	updated_tc = tc+1
	info_dict[i].update({'total_changes': updated_tc})
	ct.append(change_type)
	info_dict[i].update({'change_types': ct})
	return info_dict[i],updated_tc


def remove(ct, info_dict, i):
	tc = info_dict[i]['total_changes']
	updated_tc = tc+1
	ct.append('CR')
	info_dict[i].update({'total_changes': updated_tc})
	info_dict[i].update({'change_types': ct})
	info_dict[i]['new_attributes'] = "NA"
	info_dict[i]['new_bounds'] = "NA"
	info_dict[i]['class'] = info_dict[i]['node_attributes']['class'].split(".")[-1]
	return info_dict


def locate_old_component(template, image,i):
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
	(height, width, C) = template.shape
	cropped_component = cv2.resize(cropped_component, (width, height))
	gray_cropped_component = cv2.cvtColor(cropped_component, cv2.COLOR_BGR2GRAY)
	canny_gray_cropped_component = cv2.Canny(gray_cropped_component, 100,200, apertureSize=3)

	ssim_score = ssim(canny_gray_template,canny_gray_cropped_component,full=True)[0]
	if ssim_score > 0.75: 
		locator_flag = True
	else:
		locator_flag = False
	
	return locator_flag, startX, startY, endX, endY



def crop_old_component(dp,p,component_boundary,tv):
	oldGUI_directory = metadata + app_versions[p].split("/")[0] +"/"+ 'old_ss_comps'
	old_ss_path = dp[0]
	old_ss = cv2.imread(old_ss_path)
	oldGUI_components = {}
	for i in component_boundary:
		x = int(component_boundary[i][0])
		y = int(component_boundary[i][1])
		w = int(component_boundary[i][2])
		h = int(component_boundary[i][3])
		component = old_ss[y:h, x:w]
		oldGUI_components[i] = [x,y,w,h]
		if not os.path.exists(oldGUI_directory):
			os.makedirs(oldGUI_directory)
		cv2.imwrite(oldGUI_directory+'/['+str(tv)+"]_old-"+str(i)+".png",component)
	return oldGUI_directory, oldGUI_components



def get_record(dp, p, info_dict, old_comp_boundaries, tv):
	filename = metadata + app_versions[p].split("/")[0] +"/"+ '['+str(tv)+"]_basic_info.csv"
	old_png = cv2.imread(dp[0])
	new_png = cv2.imread(dp[2])
	oldGUI_directory, oldGUI_components = crop_old_component(dp,p,old_comp_boundaries,tv)
	df = pd.read_csv(filename)

	#df[5] --> node_num is 6
	#info_dict[5] --> node_num is 5

	for i in oldGUI_components:
		ct = []
		changed = False
		component_type = info_dict[i]['node_attributes']['class'].split(".")[-1]
		resource_id = info_dict[i]['node_attributes']['resource-id']

		template = cv2.imread(oldGUI_directory+'/['+str(tv)+"]_old-"+str(i)+'.png')
		old_x = oldGUI_components[i][0]
		old_y = oldGUI_components[i][1]
		old_w = oldGUI_components[i][2]
		old_h = oldGUI_components[i][3]

		if template.shape[0] == 1794 and template.shape[1] == 1080:
			locator_flag = True
			color_changed_flag = False
			new_x, new_y, new_w, new_h = 0,0,1080,1794
		
		elif template.shape[0] == 1731 and template.shape[1] == 1080:
			locator_flag = True
			color_changed_flag = False
			new_x, new_y, new_w, new_h = 0,63,1080,1794
		
		elif template.shape[0] > 7 and template.shape[1] > 7:
			color_changed_flag, ssim_score = check_for_color_changes(new_png, template, old_x, old_y, old_w, old_h, i)
			content_similar = ssim_score > tv
			if content_similar:
				locator_flag,new_x,new_y,new_w,new_h = True, old_x, old_y, old_w, old_h
			else:
				locator_flag,new_x,new_y,new_w, new_h= locate_old_component(template, new_png,i)
				if locator_flag:
					color_changed_flag, ssim_score = check_for_color_changes(new_png,template,new_x,new_y,new_w,new_h,i)
				else:
					pass
		else:
			pass

		if not locator_flag:
			info_dict = remove(ct, info_dict, i)
		
		if locator_flag:
			if new_h>1794 and new_h<= 1920:
				info_dict = remove(ct,info_dict, i)
			else:
				new_bounds = '['+str(new_x)+','+str(new_y)+']['+str(new_w)+','+str(new_h)+']'
				info_dict[i].update({'new_bounds':new_bounds})
				temp = info_dict[i]['node_attributes']
				info_dict[i]['new_attributes'] = copy.deepcopy(info_dict[i]['node_attributes'])
				info_dict[i]['new_attributes'].update({'bounds':info_dict[i]['new_bounds']})
				tc = info_dict[i]['total_changes']
				if (component_type == 'ImageView' or component_type == 'ImageButton'):
					old_text = info_dict[i]['node_attributes']['text']
					if old_text == "" and color_changed_flag == True:
						info_dict[i],tc = update(tc, info_dict, i, ct, 'CC')
					if old_text != "" and color_changed_flag == True:
						old_comp = old_png[old_y:old_h, old_x:old_w]
						new_comp = new_png[new_y:new_h, new_x:new_w]
						old_text = info_dict[i]['node_attributes']['text']
						text_changed, text_color_changed, new_text = text.detect_text_changes(old_comp, new_comp)
						if text_changed:
							info_dict[i]['new_attributes'].update({'text':new_text})
							info_dict[i],tc = update(tc, info_dict, i, ct, 'IC')
						else:
							info_dict[i],tc = update(tc, info_dict, i, ct, 'CC')
					if old_text != "" and color_changed_flag == False:
						old_comp = old_png[old_y:old_h, old_x:old_w]
						new_comp = new_png[new_y:new_h, new_x:new_w]
						old_text = info_dict[i]['node_attributes']['text']
						text_changed, text_color_changed, new_text = text.detect_text_changes(old_comp, new_comp)
						if text_changed:
							info_dict[i]['new_attributes'].update({'text':new_text})
							info_dict[i],tc = update(tc, info_dict, i, ct, 'IC')


				if df['isParent'][i-1] == 'Leaf' and (component_type == "TextView" or component_type == 'Button'):
					old_comp = old_png[old_y:old_h, old_x:old_w]
					new_comp = new_png[new_y:new_h, new_x:new_w]
					old_text = info_dict[i]['node_attributes']['text']
					text_changed, text_color_changed, new_text = text.detect_text_changes(old_comp, new_comp)
					if text_changed:
						info_dict[i]['new_attributes'].update({'text':new_text})
						info_dict[i],tc = update(tc, info_dict, i, ct, 'TC')
					if text_color_changed:
						info_dict[i],tc = update(tc, info_dict, i, ct, 'TXC')

					
				#if component x position has been changed:
				if old_x != new_x:
					info_dict[i],tc = update(tc, info_dict, i, ct, 'HT')

				#if component y position has been changed:
				if old_y != new_y:
					info_dict[i],tc = update(tc, info_dict, i, ct, 'VT')

				#if component height has been changed:
				if old_h != new_h:
					info_dict[i],tc = update(tc, info_dict, i, ct, 'VS')

				#if component width has been changed:
				if old_w != new_w:
					info_dict[i],tc = update(tc, info_dict, i, ct, 'HS')
			
				#if component color has been changed:
				if color_changed_flag == True and component_type != 'ImageButton':
					info_dict[i],tc = update(tc, info_dict, i, ct, 'CC')
				
				info_dict[i]['class'] = component_type
	
	records = []
	for i in range(1,len(info_dict)+1):
		records.append(info_dict[i])
	return records, info_dict


