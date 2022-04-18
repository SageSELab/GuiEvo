from config import *
import csv  
import pandas as pd
import itertools 




def set_parent_leaf_tag(nodes,index_level_pairs,df,filename):
	parent_locations = []
	node_nums = []
	leaf_nodes = []
	for i in range (len(nodes)):
		parent_locations.append(nodes[i][3])
	for i in range (len(nodes)):
		node_index_level = index_level_pairs[i]
		if node_index_level in parent_locations:
			node_nums.append(int(nodes[i][0]))
		if node_index_level not in parent_locations:
			leaf_nodes.append(int(nodes[i][0]))
	for loc in node_nums:
		df.loc[df["node_num"]==loc, "isParent"] = "Parent"
	for i in range(len(leaf_nodes)):
		df.at[leaf_nodes[i]-1, 'isParent'] = "Leaf"
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



def get_valid_nodes(csv_filename):
	nodes = []
	with open(csv_filename) as fileObject:
		readerObject = csv.reader(fileObject)
		for row in readerObject:
			nodes.append(row)
	nodes = nodes[2:]
	return nodes



def get_parent_leaf_tag(root_directory):
	filename = root_directory + csv_filename
	nodes = get_valid_nodes(filename)
	index_level_pairs = get_index_level_pairs(nodes)
	df = pd.read_csv(filename)
	set_parent_leaf_tag(nodes,index_level_pairs,df,filename)

