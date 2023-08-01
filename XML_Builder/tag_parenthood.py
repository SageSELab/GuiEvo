from config import *
import csv  
import pandas as pd
import itertools 

	


def set_parent_node_num(filename):
	df = pd.read_csv(filename)
	df.loc[0,'parent_node_num'] = 0
	df.loc[1,'parent_node_num'] = 1
	
	for i in range(len(df)): # for looping over parent locations 
		if i>1:
			parent_location = df.loc[i,'parent_location'] # string form (0, '4') where 0 is parent level and '4' is parent index and both 0 and 4 are in string form
			parent_level = parent_location.split(',')[0].replace('(','') #in string form
			parent_index = parent_location.split(',')[1].replace(')','').replace(' ','').strip("'") #in string form
			parent_node_nums = []	
			for j in range(1,i): # for looping over node level and index
				node_level = str(df.loc[j,'xml_level'])
				node_index = str(df.loc[j,'xml_index'])
				if(node_level == parent_level and node_index == parent_index):
					parent_node_nums.append(df.loc[j,'node_num'])
			node_num = parent_node_nums[len(parent_node_nums)-1]
			df.loc[i,'parent_node_num'] = node_num
	df.to_csv(filename, index=False)




def set_parent_leaf_tag(filename):
	set_parent_node_num(filename)
	df = pd.read_csv(filename)
	parent_node_nums = []
	for i in range (1,len(df)):
		parent_node_nums.append(df.loc[i,'parent_node_num'])
	for node in parent_node_nums:
		df.loc[df["node_num"] == node, "isParent"] = "Parent"
	for i in range (1,len(df)):
		if df.loc[i,'isParent'] != "Parent":
			df.loc[i,'isParent'] = "Leaf"
	df.loc[0,'isParent'] = None
	df['xml_index'].astype(int)
	df['xml_index'].astype(str)
	df['total_changes'].astype(float)
	df['total_changes'].astype(int)
	df.to_csv(filename, index=False)
	




#this function tags the nodes as parent if they have child(ren)
def get_index_level_pairs(nodes):
	index_level_pairs = []	
	for i in range (len(nodes)):
		level = nodes[i][1]
		index = nodes[i][2]
		index_level_pairs.append("("+level+", '"+index+"')")
	return index_level_pairs



def get_valid_nodes(filename):
	nodes = []
	with open(filename) as fileObject:
		readerObject = csv.reader(fileObject)
		for row in readerObject:
			nodes.append(row)
	nodes = nodes[2:]
	return nodes



def get_parent_leaf_tag(filename):
	nodes = get_valid_nodes(filename)
	index_level_pairs = get_index_level_pairs(nodes)
	df = pd.read_csv(filename)
	set_parent_leaf_tag(filename)

