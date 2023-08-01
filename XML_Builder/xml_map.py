import xml.etree.ElementTree as ET
import numpy as np

component_list = []

#https://stackoverflow.com/questions/15748528/python-how-to-determine-hierarchy-level-of-parsed-xml-elements
def perf_func(elem, func, level=0):
	func(elem,level)
	for child in list(elem):
		perf_func(child, func, level+1)


def print_level(elem,level):
	index = elem.get("index")
	attributes = elem.attrib
	component_list.append((level,index,attributes))


def get_component_list(old_xml):
	root = ET.parse(old_xml) #root of the parsed XML tree
	perf_func(root.getroot(), print_level)
	tree = np.empty([len(component_list),5],dtype=object)
	return component_list, tree

	
def parent_to_child(old_xml):
	nodes_list, tree = get_component_list(old_xml)
	total_nodes = len(nodes_list)	#total number of nodes in the XML tree
	i = 0
	tc = 0	#total number of changes for any component
	info_dict = {}	#dictionary for holding the information
	for ind in range(total_nodes):
		if nodes_list[ind][1]==None:
			tree[i][0] = i+1 # node_num
			tree[i][1] = nodes_list[ind][0] #level
			tree[i][2] = nodes_list[ind][1] #index
			tree[i][3] = None #parent_level_index
			tree[i][4] = None #attributes
			info_dict[tree[i][0]] = {'node_num':tree[i][0],'xml_level':tree[i][1],'xml_index':'0','parent_location':tree[i][3],'node_attributes':tree[i][4],'component_validity':'ignored','total_changes':tc,'class':None}
			i += 1
		else:
			tree[i][0] = i+1 # node_num
			tree[i][1] = nodes_list[ind][0] #level
			tree[i][2] = nodes_list[ind][1] #index
			tree[i][4] = nodes_list[ind][2] #attributes
			parent_level = tree[i][1] - 1
			if tree[i][1] == 1:
				parent_index = '0'
				tree[i][3] = (parent_level,parent_index) #parent_level_index
				info_dict[tree[i][0]] = {}
				info_dict[tree[i][0]]['node_attributes'] = {}
				info_dict[tree[i][0]] = {'node_num':tree[i][0],'xml_level':tree[i][1],'xml_index':tree[i][2],'parent_location':tree[i][3],'node_attributes':tree[i][4],'total_changes':tc}
				i+=1
			else:
				indlist = []
				for j in range (1,i):
					if nodes_list[j][0] == parent_level:
						indlist.append(nodes_list[j][1])
				parent_index = indlist[len(indlist)-1]
				tree[i][3] = (parent_level,parent_index)  #parent_level_index
				info_dict[tree[i][0]] = {}
				info_dict[tree[i][0]]['node_attributes'] = {}
				info_dict[tree[i][0]] = {'node_num':tree[i][0],'xml_level':tree[i][1],'xml_index':tree[i][2],'parent_location':tree[i][3],'node_attributes':tree[i][4],'total_changes':tc}
				i+=1	
	global component_list
	component_list = []
	return info_dict, tree



