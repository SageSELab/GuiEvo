from config import *
import glob
import os
import re
import pandas as pd
import XML_Builder.create_csvfile as csv_generator
import XML_Builder.xml_map as xml_map
import XML_Builder.boundary_retrieval as node_bounds
import XML_Builder.tag_parenthood as tag_parenthood
import XML_Builder.dynxml_builder as xml_generator
import Detection.layout as layout
import Detection.resource as resource
import Evaluation.getgtinfo as gt
import Evaluation.compileresult as rq1
import Evaluation.ted as rq2 
import Evaluation.compare_with_baseline as rq3_4
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim



def evaluate_rq4():
	rq3_4.compare_XMLs(GuiEvo,REMAUI,ReDraw)
	print("9. RQ4 evaluation done")



def evaluate_rq3():
	rq3_4.compare_screens(GuiEvo,REMAUI)
	print("8. RQ3 evaluation done")
	


def evaluate_rq2(dp, p, tv):
	path = metadata + app_versions[p].split("/")[0]
	new_xml = dp[3]
	distance = rq2.get_ted(new_xml,path+"/"+'['+str(tv)+']_dynamic.xml')
	print("7. RQ2 evaluation done")
	return distance


def evaluate_rq1(dp, p, groundtruth,tv):
	path = metadata + app_versions[p].split("/")[0]
	compiled_tool_result = rq1.compile_tool_result(path,tv)
	change_wise_result, rq1_result = rq1.get_confusion_matrix(compiled_tool_result,groundtruth,path)
	print("6. RQ1 evaluation done")
	return (change_wise_result, rq1_result)



def form_groundtruth(dp, p):
	package_name = app_versions[p]
	gt_xml = evaluation_data_directory + package_name +"/"+ package_name.split("/")[0] + ".xml"
	gt_csv = metadata + package_name.split("/")[0] +"/"+ package_name.split("/")[0] + ".csv"
	combined_info = gt.extract_info(gt_xml)
	csv_generator.gt_generate(gt_csv)
	csv_generator.gt_save(gt_csv, combined_info)
	groundtruth = pd.read_csv(gt_csv)
	print("5. Groundtruth CSV generated")
	return groundtruth



def form_dynamicxml(dp,p,tv):
	path = metadata + app_versions[p].split("/")[0] +"/"
	filename = path + '['+str(tv)+"]_dynamic_xml_base.csv"
	xml_generator.generate_xml(filename,path,tv)
	print("4. Dynamic XML formed")



def detect_changes(dp, p, info_dict, old_comp_boundaries, tv):
	records_layout_changes, updated_dict = layout.get_record(dp, p, info_dict, old_comp_boundaries, tv)
	filename = metadata + app_versions[p].split("/")[0] +"/"+ '['+str(tv)+"]_basic_info.csv"
	csv_generator.save(filename, records_layout_changes)
	tag_parenthood.get_parent_leaf_tag(filename)
	print("2. Layout and Text changes detected")
	metadata_dir = metadata + app_versions[p].split("/")[0]
	records_resource_changes = resource.list_changes(dp,metadata_dir,updated_dict,tv)
	print("3. Resource changes detected")
	


def map_parent_child(dp, p, tv):
	if not os.path.exists(metadata + app_versions[p].split("/")[0]):
		os.makedirs(metadata + app_versions[p].split("/")[0])
	filename = metadata + app_versions[p].split("/")[0] +"/["+str(tv)+"]_basic_info.csv"
	csv_generator.build_tree(filename)
	info_dict, tree = xml_map.parent_to_child(dp[1]) #passing old_xml
	info_dict, old_comp_boundaries, records = node_bounds.get_boundaries(info_dict, tree)
	csv_generator.save(filename, records)
	tag_parenthood.get_parent_leaf_tag(filename)
	print("1. Parent-child mapping done")
	return info_dict, old_comp_boundaries




#this function will return a list of quadruples that will contain four inputs for each app.
#each quadruple is considered as one data point.
def form_data_points():
	data_points = []
	for i in range(total_apps):
		point = []
		point.append(evaluation_data_directory+app_versions[i]+"/"+inputs[0])	#old_ss
		point.append(evaluation_data_directory+app_versions[i]+"/"+inputs[1])	#old_xml
		point.append(evaluation_data_directory+app_versions[i]+"/"+inputs[2])	#new_ss
		point.append(evaluation_data_directory+app_versions[i]+"/"+inputs[3])	#new_xml
		data_points.append(point)
	return data_points


if __name__ == '__main__':
	
	data_points = form_data_points()
	if not os.path.exists(metadata):
		os.makedirs(metadata)
	p = 0

	rq1_results = {} 
	rq2_results = {}
	iou_results = []

	appnames = []
	app_records = []

	p = 0	
	for dp in data_points:
		appname = app_versions[p].split("/")[0]
		threshold_value = threshold_values[appname]
		print(appname)
		print("---------------------------------")
		
		rq1_results[appname] = {}
		rq2_results[appname] = {}
		info_dict, old_comp_boundaries = map_parent_child(dp, p, threshold_value)
		detect_changes(dp, p, info_dict, old_comp_boundaries, threshold_value)
		form_dynamicxml(dp,p,threshold_value)
		groundtruth = form_groundtruth(dp,p)
		rq1_results[appname] = evaluate_rq1(dp,p,groundtruth,threshold_value)
		rq2_results[appname] = evaluate_rq2(dp,p,threshold_value)
		p += 1
		appnames.append(appname)
	
	rows = []
	for appname in appnames:
		threshold_value = threshold_values[appname]
		avg_results = {}
		metric_results = rq1_results[appname][1]
		row = {'App': appname,'Threshold': threshold_value,**rq1.output_app_results(rq1_results[appname][0],rq1_results[appname][1],rq2_results[appname])}
		rows.append(row)
	
	df = pd.DataFrame(rows)
	df.to_excel('results.xlsx', index=False)

	
	rq1_appwise_result = []
	rq2_appwise_result = []
	
	for appname in appnames:
		rq1_appwise_result.append(rq1_results[appname])
		rq2_appwise_result.append(rq2_results[appname])

	typewise_overall_accuracy, typewise_overall_precision, typewise_overall_recall, typewise_overall_f1, appwise_overall_accuracy, appwise_overall_precision, appwise_overall_recall, appwise_overall_f1 = rq1.get_overall_avg_result(total_apps, rq1_appwise_result)
	print('Typewise Overall Average Results\n')
	print('average accuracy:', typewise_overall_accuracy)
	print('average precision:', typewise_overall_precision)
	print('average recall:', typewise_overall_recall)
	print('average f1-score:', typewise_overall_f1)

	print('Appwise Overall Average Results\n')
	print('average accuracy:', appwise_overall_accuracy)
	print('average precision:', appwise_overall_precision)
	print('average recall:', appwise_overall_recall)
	print('average f1-score:', appwise_overall_f1)
	
	print('average tree edit distance:', sum(rq2_appwise_result)/total_apps)
	
	evaluate_rq3()
	evaluate_rq4()
	