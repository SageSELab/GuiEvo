from config import *


def get_boundaries(info_dict, xmltree):
	component_boundary = {}
	tc = 0
	for i in range (len(xmltree)):
		if xmltree[i][2]!=None and xmltree[i][4]["bounds"]!='[0,0][0,0]' and xmltree[i][4]["bounds"]!='[0,0][1080,63]':
			#boundaries are in [x,y][width,height] format
			component_boundary[xmltree[i][0]] = xmltree[i][4]["bounds"].replace("][",",").replace("[","").replace("]","").strip().split(",")
			info_dict[xmltree[i][0]].update({'component_validity':'valid','old_bounds': xmltree[i][4]["bounds"],'new_bounds': xmltree[i][4]["bounds"],'total_changes':tc,'change_types': "NC",'change_description': "No changes",'new_attributes': xmltree[i][4]})
			
		elif xmltree[i][2]!=None and (xmltree[i][4]["bounds"]=='[0,0][0,0]' or xmltree[i][4]["bounds"]=='[0,0][1080,63]'):
			info_dict[xmltree[i][0]].update({'component_validity':'ignored','old_bounds': xmltree[i][4]["bounds"],'new_bounds': xmltree[i][4]["bounds"],'total_changes':tc,'change_types': "NC",'change_description': "No changes",'new_attributes': xmltree[i][4]})
	
	records = []
	for i in range(1,len(info_dict)+1):
		records.append(info_dict[i])
	return info_dict, component_boundary, records