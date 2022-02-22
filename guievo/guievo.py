import cv2
import numpy as np
from matplotlib import pyplot as plt
import xml.etree.ElementTree as ET
import xml.sax as sax
import xml.sax.handler as saxhandler
from xml.dom import minidom
from dicttoxml import dicttoxml
import re
import os
import path
import csv  
import copy
import imutils
from PIL import Image
import imagehash
import pandas as pd 


app = str(2)
old_GUI = cv2.imread(app+'/old.png')
new_GUI = cv2.imread(app+'/new.png')
old_xml = app+'/old.xml'
xml_tree = ET.parse(old_xml)
csv_filename = "gui_changes.csv"
root = '/Users/sabihasalma/Documents/Academic/Research/GUIEvo/'

#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#														CREATING CSV FILE TO STORE XML TREE INFORMATION AND GUI CHANGES 								   |
#__________________________________________________________________________________________________________________________________________________________|

#The CSV file will contain the following information for all the components from old GUI and new GUI. Example info is in the following line.
#node_num, xml_level, xml_index, parent_location, node_attributes, component_validity,   old_bounds,    	new_bounds, 	total_changes, change_types, change_description, new_attributes
#	3,			2,		 '0'	   (1,'0')			  {...}				valid 	  	  [0,0][1080,1794]	 [0,3][1080,1794]			1 			 RC 	 component removed		  {...}


tc = 0
info_dict = {}
header = ['node_num','xml_level','xml_index','parent_location','node_attributes','component_validity','old_bounds','new_bounds','total_changes','change_types','change_description','new_attributes']

def check_dir(file_name):
	directory = os.path.dirname(file_name)
	if not os.path.exists(directory):
		os.makedirs(directory)

def save(file_name, records):
	check_dir(file_name)
	csv_file = open(file_name,'w+')
	csvWriter = csv.writer(csv_file,delimiter=',')
	count = 0
	for record in records:
		csvWriter.writerow([record])
		count+=1
	#print(count, " record/s saved to ",file_name)
	
report_directory = os.path.abspath(os.path.join(app+"/GUI_Changes"))
#save(report_directory+"/"+csv_filename, [header])

#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#															 XML TREE CONSTRUCTION WITH CHILD-TO-PARENT MAPPING 										   |
#__________________________________________________________________________________________________________________________________________________________|


#XML Tree Construction with Parent-Child Mapping

root = ET.parse(old_xml)
component_list = []
	
def construct_tree(nodes_list,total_nodes):
	i = 0
	tree_root = ET.parse(old_xml)

	for ind in range(len(nodes_list)):
		if nodes_list[ind][1]==None:
			xmltree[i][0] = i+1 # node_num
			xmltree[i][1] = nodes_list[ind][0] #level
			xmltree[i][2] = nodes_list[ind][1] #index
			xmltree[i][3] = None #parent_level_index
			xmltree[i][4] = None #attributes
			info_dict[xmltree[i][0]] = {'node_num':xmltree[i][0],'xml_level':xmltree[i][1],'xml_index':xmltree[i][2],'parent_location':xmltree[i][3],'node_attributes':xmltree[i][4],'component_validity':'ignored','old_bounds': "NA",'new_bounds': "NA",'total_changes':"NA",'change_types':"NA",'change_description':"NA",'new_attributes':"NA"}
			#print(xmltree[0][0],xmltree[0][1],xmltree[0][2],xmltree[0][4], xmltree[0][3])
			#print(xmltree[i][0],xmltree[i][4])
			i += 1
		else:
			xmltree[i][0] = i+1 # node_num
			xmltree[i][1] = nodes_list[ind][0] #level
			xmltree[i][2] = nodes_list[ind][1] #index
			xmltree[i][4] = nodes_list[ind][2] #attributes
			parent_level = xmltree[i][1] - 1
			if xmltree[i][1] == 1:
				parent_index = None
				xmltree[i][3] = (parent_level,parent_index) #parent_level_index
				info_dict[xmltree[i][0]] = {}
				info_dict[xmltree[i][0]]['node_attributes'] = {}
				info_dict[xmltree[i][0]] = {'node_num':xmltree[i][0],'xml_level':xmltree[i][1],'xml_index':xmltree[i][2],'parent_location':xmltree[i][3],'node_attributes':xmltree[i][4],'total_changes':tc}
				#print(xmltree[i][0],xmltree[i][1],xmltree[i][2],xmltree[i][4]['bounds'], xmltree[i][3])
				#print(xmltree[i][0],xmltree[i][4]['bounds'])
				i+=1
			else:
				indlist = []
				for j in range (1,i):
					if nodes_list[j][0] == parent_level:
						indlist.append(nodes_list[j][1])
				parent_index = str(indlist[len(indlist)-1])
				xmltree[i][3] = (parent_level,parent_index)  #parent_level_index
				info_dict[xmltree[i][0]] = {}
				info_dict[xmltree[i][0]]['node_attributes'] = {}
				info_dict[xmltree[i][0]] = {'node_num':xmltree[i][0],'xml_level':xmltree[i][1],'xml_index':xmltree[i][2],'parent_location':xmltree[i][3],'node_attributes':xmltree[i][4],'total_changes':tc}
				#print(xmltree[i][0],xmltree[i][1],xmltree[i][2],xmltree[i][4]['bounds'], xmltree[i][3])
				#print(xmltree[i][0],xmltree[i][4]['bounds'])
				i+=1	

#perf_func() and print_level() have been used from 
#https://stackoverflow.com/questions/15748528/python-how-to-determine-hierarchy-level-of-parsed-xml-elements
def perf_func(elem, func, level=0):
	func(elem,level)
	for child in list(elem):
		perf_func(child, func, level+1)

def print_level(elem,level):
	index = elem.get("index")
	attributes = elem.attrib
	component_list.append((level,index,attributes))
	#print("level",level,"index",index)

perf_func(root.getroot(), print_level)
#print(component_list)
total_nodes = len(component_list)
xmltree = np.empty([total_nodes,5],dtype=object)

construct_tree(component_list,total_nodes)




#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#															 XML COMPONENT BOUNDARY RETRIEVAL 															   |
#__________________________________________________________________________________________________________________________________________________________|

#XML component boundary retrieval
#print("\n",len(xmltree),"\n")
component_boundary = {}
for i in range (len(xmltree)):
	if xmltree[i][2]!=None and xmltree[i][4]["bounds"]!='[0,0][0,0]' and xmltree[i][4]["bounds"]!='[0,0][1080,63]':
		#boundaries are in [x,y][width,height] format
		component_boundary[xmltree[i][0]] = xmltree[i][4]["bounds"].replace("][",",").replace("[","").replace("]","").strip().split(",")
		info_dict[xmltree[i][0]].update({'component_validity':'valid','old_bounds': xmltree[i][4]["bounds"]})
		
	elif xmltree[i][2]!=None and (xmltree[i][4]["bounds"]=='[0,0][0,0]' or xmltree[i][4]["bounds"]=='[0,0][1080,63]'):
		info_dict[xmltree[i][0]].update({'component_validity':'ignored','old_bounds': xmltree[i][4]["bounds"],'new_bounds': xmltree[i][4]["bounds"],'total_changes':tc,'change_types': "NA",'change_description': "NA",'new_attributes': xmltree[i][4]})
		

#print(len(component_boundary))




#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#													COMPONENT EXTRACTION FROM OLD GUI USING OLD XML 													   |
#__________________________________________________________________________________________________________________________________________________________|

#Extraction of components from the old GUI

oldGUI_components = {}
oldGUI_directory = root+app+'/oldGUI_directory'
for i in component_boundary:
	x = int(component_boundary[i][0])
	y = int(component_boundary[i][1])
	w = int(component_boundary[i][2])
	h = int(component_boundary[i][3])
	component = old_GUI[y:h, x:w]
	oldGUI_components[i] = [x,y,w,h]
	if not os.path.exists(oldGUI_directory):
		os.makedirs(oldGUI_directory)
	#print(i, (x,y,w,h))
	cv2.imwrite(oldGUI_directory+"/old-"+str(i)+".png",component)
	

#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#												MAPPING OLD GUI COMPONENTS IN NEW GUI AND RECORD CHANGES									   			   |			
#__________________________________________________________________________________________________________________________________________________________|


#Mapping image components from old GUI into the mockup GUI
img = new_GUI
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img2 = img.copy()
prev_img = img2.copy()
mappedGUI_directory = root+app+'/mappedGUI_directory'

coords_list = {}
for i in oldGUI_components:
	template = cv2.imread(oldGUI_directory+"/old-"+str(i)+'.png',0)
	#print(i,type(template))
	#w, h = template.shape[::-1]
	h = template.shape[0]
	w = template.shape[1]
	method = 'cv2.TM_CCOEFF_NORMED'
	img = img2.copy()
	method = eval(method)
	# Apply template Matching
	res = cv2.matchTemplate(img_gray,template,method)

	threshold = 0.75
	flag = False

	loc = np.where( res >= threshold)
	for pt in zip(*loc[::-1]):
		cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (0,0,255), 1)
		flag = True
	if not os.path.exists(mappedGUI_directory):
		os.makedirs(mappedGUI_directory)
	ct = []
	cd = []
	if flag == True:
		new_x = pt[0]
		new_y = pt[1]
		new_bounds = '['+str(new_x)+','+str(new_y)+']['+str(w)+','+str(h)+']'
		if new_bounds != info_dict[i]['old_bounds']:
			info_dict[i].update({'new_bounds':new_bounds})
			temp = info_dict[i]['node_attributes']
			info_dict[i]['new_attributes'] = copy.deepcopy(info_dict[i]['node_attributes'])
			info_dict[i]['new_attributes'].update({'bounds':info_dict[i]['new_bounds']})
		if x != new_x:
			tc = info_dict[i]['total_changes']
			updated_tc = tc+1
			info_dict[i].update({'total_changes': updated_tc})
			ct.append('HT')
			cd.append('Component has been horizontally translated')
			info_dict[i].update({'change_types': ct})
			info_dict[i].update({'change_description': cd})
		if y != new_y:
			tc = info_dict[i]['total_changes']
			updated_tc = tc+1
			info_dict[i].update({'total_changes': updated_tc})
			ct.append('VT')
			cd.append('Component has been vertically translated')
			info_dict[i].update({'change_types': ct})
			info_dict[i].update({'change_description': cd})
		cv2.imwrite(mappedGUI_directory+'/res-'+str(i)+'.png',img)
	elif flag == False:
		tc = info_dict[i]['total_changes']
		updated_tc = tc+1
		ct.append('CR')
		cd.append('Component has been removed')
		info_dict[i].update({'total_changes': updated_tc})
		info_dict[i].update({'change_types': ct})
		info_dict[i].update({'change_description': cd})
		info_dict[i]['new_attributes'] = "NA"
		info_dict[i]['new_bounds'] = "NA"
print((len(xmltree)))


report_directory = os.path.abspath(os.path.join(app+"/GUI_Changes"))
filename = 'gui_changes.csv'
directory = os.path.dirname(report_directory+'/'+filename)
if not os.path.exists(directory):
	os.makedirs(directory)
records = []
for i in range(1,len(info_dict)+1):
	records.append(info_dict[i])
with open(report_directory+'/'+filename, 'w') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames = header)
	writer.writeheader()
	writer.writerows(records)


#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#												DETECT ADDED GUI COMPONENTS IN NEW GUI AND RECORD INFORMATION								   			   |			
#__________________________________________________________________________________________________________________________________________________________|


def is_template_in_image(img, templ):
    result = cv2.matchTemplate(img, templ, cv2.TM_SQDIFF)
    min_val = cv2.minMaxLoc(result)[0]
    thr = 10e-6
    return min_val <= thr

x = 0
y = 63
w = 1080
h = 1920

diffGUI_directory = root+app+'/diffGUI_directory'
if not os.path.exists(diffGUI_directory):
	os.makedirs(diffGUI_directory)

new_screen = new_GUI[y:h, x:w]
old_screen = old_GUI[y:h, x:w]
im = new_screen.copy()
diff = old_screen.copy()
cv2.absdiff(old_screen, new_screen, diff)

gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
kernel = np.ones((7,7), 'uint8')
for i in range(0, 3):
	dilated = cv2.dilate(gray.copy(), kernel, iterations= i+1)

(T, thresh) = cv2.threshold(dilated, 3, 255, cv2.THRESH_BINARY)
cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

bounds = {}
count = 1
for c in cnts:
# nicely fiting a bounding box to the contour
	(x, y, w, h) = cv2.boundingRect(c)
	crop_img = new_screen[y:y+h, x:x+w]
	if not is_template_in_image(old_screen,crop_img):
		bounds[count] = '['+str(x)+','+str(y)+']['+str(w)+','+str(h)+']'	
	cv2.imwrite(diffGUI_directory+"/diff-"+str(count)+".png",crop_img)
	cv2.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 3)	
	count += 1

cv2.imwrite(diffGUI_directory+"/changes.png", im)
for i in bounds.keys():
	im = bounds[i]
	crop_img = im.replace("][",",").replace("[","").replace("]","").strip().split(",")
	x = int(crop_img[0])
	y = int(crop_img[1])
	w = int(crop_img[2])
	h = int(crop_img[3])
	cv2.imwrite(diffGUI_directory+"/new-"+str(i)+".png",new_screen[y:y+h, x:x+w])

added_components = {}

for i in component_boundary:
	old_comp = cv2.imread(oldGUI_directory+"/old-"+str(i)+".png")
	hash0 = imagehash.average_hash(Image.open(oldGUI_directory+'/old-'+str(i)+'.png')) 
	for j in bounds.keys():
		diff_comp = cv2.imread(diffGUI_directory+"/new-"+str(j)+".png")
		hash1 = imagehash.average_hash(Image.open(diffGUI_directory+"/new-"+str(j)+".png"))
		dim = (diff_comp.shape[1], diff_comp.shape[0])
		similar = False
		resized_old_comp = cv2.resize(old_comp, dim, interpolation = cv2.INTER_AREA)
		cutoff_min = 15
		cutoff_max = 25
		if not is_template_in_image(diff_comp,resized_old_comp):
			print("diff_comp-"+str(j)+": "+str(hash1 - hash0)+"with cutoff range "+str(cutoff_min)+"-"+str(cutoff_max))
				
			if hash0 - hash1 > cutoff_min and hash0 - hash1 < cutoff_max:
				similar = False

	if not similar:
		cv2.imwrite("new-"+str(j)+".png",diff_comp)
		added_components[j] = copy.deepcopy(bounds[j])

for i in added_components.keys():
	print(added_components[i])


#----------------------------------------------------------------------------------------------------------------------------------------------------------|
#														SET PARENT NODES FOR ADDED GUI COMPONENTS 							 				  			   |			
#__________________________________________________________________________________________________________________________________________________________|

"""
filename = open(report_directory+"/"+csv_filename)
header = ['node_num','xml_level','xml_index','parent_location','node_attributes','component_validity','old_bounds','new_bounds','total_changes','change_types','change_description','new_attributes']
df = pd.read_csv(report_directory+"/"+csv_filename,index_col =False,usecols = header)
df['xml_index'] = df['xml_index'].astype(str)
"""
"""
parent_node_bounds = []
print(info_dict[xmltree[0][0]]['parent_location'])
print(info_dict[xmltree[1][0]]['parent_location'])
print(info_dict[xmltree[2][0]]['parent_location'])

None
(0, None)
(1, '0')

for i in range (len(xmltree)):
	if i == 0:
		continue
	if i == 1:
		parent_node_bounds.append(info_dict[xmltree[1][0]]['new_bounds'])
	else:
		parent_level = info_dict[xmltree[i][0]]['parent_location'][0]
		parent_index = info_dict[xmltree[i][3]]['parent_location'][1]
		for j in range(2,i):
			if parent_index == None:
				parent_node_bounds.append(info_dict[xmltree[1][0]]['new_bounds'])
			elif info_dict[xmltree[j][0]]['xml_level'] == parent_level and info_dict[xmltree[j][0]]['xml_index'] == parent_index:
				parent_node_bounds.append(info_dict[xmltree[j][0]]['new_bounds'])
print(parent_node_bounds)
"""
