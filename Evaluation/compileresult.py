from config import *
import xml.etree.ElementTree as ET
import glob
import os
import pathlib
import pandas as pd
import numpy as np
from collections import Iterable
import re
import copy


"""
True positive (TP): Correctly predicting the positive class
True Negative (TN): Correctly predicting the negative class
False Positive (FP): Incorrectly predicting the positive class
False Negative (FN): Incorrectly predicting the negative class
"""

def output_app_results(typewise_result, avg_result, ted):
	app_result = {}
	app_result['TC_Accuracy'] = typewise_result[0][1]
	app_result['TC_Precision'] = typewise_result[0][2]
	app_result['TC_Recall'] = typewise_result[0][3]
	app_result['TC_F1'] = typewise_result[0][4]

	app_result['TXC_Accuracy'] = typewise_result[1][1]
	app_result['TXC_Precision'] = typewise_result[1][2]
	app_result['TXC_Recall'] = typewise_result[1][3]
	app_result['TXC_F1'] = typewise_result[1][4]


	app_result['HT_Accuracy'] = typewise_result[2][1]
	app_result['HT_Precision'] = typewise_result[2][2]
	app_result['HT_Recall'] = typewise_result[2][3]
	app_result['HT_F1'] = typewise_result[2][4]

	app_result['HS_Accuracy'] = typewise_result[3][1]
	app_result['HS_Precision'] = typewise_result[3][2]
	app_result['HS_Recall'] = typewise_result[3][3]
	app_result['HS_F1'] = typewise_result[3][4]

	app_result['VT_Accuracy'] = typewise_result[4][1]
	app_result['VT_Precision'] = typewise_result[4][2]
	app_result['VT_Recall'] = typewise_result[4][3]
	app_result['VT_F1'] = typewise_result[4][4]

	app_result['VS_Accuracy'] = typewise_result[5][1]
	app_result['VS_Precision'] = typewise_result[5][2]
	app_result['VS_Recall'] = typewise_result[5][3]
	app_result['VS_F1'] = typewise_result[5][4]

	app_result['CC_Accuracy'] = typewise_result[6][1]
	app_result['CC_Precision'] = typewise_result[6][2]
	app_result['CC_Recall'] = typewise_result[6][3]
	app_result['CC_F1'] = typewise_result[6][4]

	app_result['CA_Accuracy'] = typewise_result[7][1]
	app_result['CA_Precision'] = typewise_result[7][2]
	app_result['CA_Recall'] = typewise_result[7][3]
	app_result['CA_F1'] = typewise_result[7][4]

	app_result['CR_Accuracy'] = typewise_result[8][1]
	app_result['CR_Precision'] = typewise_result[8][2]
	app_result['CR_Recall'] = typewise_result[8][3]
	app_result['CR_F1'] = typewise_result[8][4]

	app_result['IC_Accuracy'] = typewise_result[9][1]
	app_result['IC_Precision'] = typewise_result[9][2]
	app_result['IC_Recall'] = typewise_result[9][3]
	app_result['IC_F1'] = typewise_result[9][4]

	app_result['AVG_Accuracy'] = avg_result[0]
	app_result['AVG_Precision'] = avg_result[1]
	app_result['AVG_Recall'] = avg_result[2]
	app_result['AVG_F1'] = avg_result[3]
	app_result['AVG_TED'] = ted
	
	return app_result


def get_overall_avg_result(total_apps, rq1_results):
	total_tc_instances, summed_tc_accuracy, summed_tc_precision, summed_tc_recall, summed_tc_f1 = 0,0,0,0,0
	total_txc_instances, summed_txc_accuracy, summed_txc_precision, summed_txc_recall, summed_txc_f1 = 0,0,0,0,0
	total_ht_instances, summed_ht_accuracy, summed_ht_precision, summed_ht_recall, summed_ht_f1 = 0,0,0,0,0
	total_hs_instances, summed_hs_accuracy, summed_hs_precision, summed_hs_recall, summed_hs_f1 = 0,0,0,0,0
	total_vt_instances, summed_vt_accuracy, summed_vt_precision, summed_vt_recall, summed_vt_f1 = 0,0,0,0,0
	total_vs_instances, summed_vs_accuracy, summed_vs_precision, summed_vs_recall, summed_vs_f1 = 0,0,0,0,0
	total_cc_instances, summed_cc_accuracy, summed_cc_precision, summed_cc_recall, summed_cc_f1 = 0,0,0,0,0
	total_ca_instances, summed_ca_accuracy, summed_ca_precision, summed_ca_recall, summed_ca_f1 = 0,0,0,0,0
	total_cr_instances, summed_cr_accuracy, summed_cr_precision, summed_cr_recall, summed_cr_f1 = 0,0,0,0,0
	total_ic_instances, summed_ic_accuracy, summed_ic_precision, summed_ic_recall, summed_ic_f1 = 0,0,0,0,0

	app_with_tc_instances, app_with_txc_instances, app_with_ht_instances, app_with_hs_instances, app_with_vt_instances, app_with_vs_instances, app_with_cc_instances, app_with_ca_instances, app_with_cr_instances, app_with_ic_instances = 0,0,0,0,0,0,0,0,0,0
	accuracy, precision, recall, f1_score = 0,0,0,0

	for i in range(0,total_apps):
		tc_instances = rq1_results[i][0][0][0]
		tc_accuracy = rq1_results[i][0][0][1]
		tc_precision = rq1_results[i][0][0][2]
		tc_recall = rq1_results[i][0][0][3]
		tc_f1 = rq1_results[i][0][0][4]
		if tc_instances > 0:
			app_with_tc_instances += 1


		txc_instances = rq1_results[i][0][1][0]
		txc_accuracy = rq1_results[i][0][1][1]
		txc_precision = rq1_results[i][0][1][2]
		txc_recall = rq1_results[i][0][1][3]
		txc_f1 = rq1_results[i][0][1][4]
		if txc_instances > 0:
			app_with_txc_instances += 1

		ht_instances = rq1_results[i][0][2][0]
		ht_accuracy = rq1_results[i][0][2][1]
		ht_precision = rq1_results[i][0][2][2]
		ht_recall = rq1_results[i][0][2][3]
		ht_f1 = rq1_results[i][0][2][4]
		if ht_instances > 0:
			app_with_ht_instances += 1

		hs_instances = rq1_results[i][0][3][0]
		hs_accuracy = rq1_results[i][0][3][1]
		hs_precision = rq1_results[i][0][3][2]
		hs_recall = rq1_results[i][0][3][3]
		hs_f1 = rq1_results[i][0][3][4]
		if hs_instances > 0:
			app_with_hs_instances += 1

		vt_instances = rq1_results[i][0][4][0]
		vt_accuracy = rq1_results[i][0][4][1]
		vt_precision = rq1_results[i][0][4][2]
		vt_recall = rq1_results[i][0][4][3]
		vt_f1 = rq1_results[i][0][4][4]
		if vt_instances > 0:
			app_with_vt_instances += 1

		vs_instances = rq1_results[i][0][5][0]
		vs_accuracy = rq1_results[i][0][5][1]
		vs_precision = rq1_results[i][0][5][2]
		vs_recall = rq1_results[i][0][5][3]
		vs_f1 = rq1_results[i][0][5][4]
		if vs_instances > 0:
			app_with_vs_instances += 1

		cc_instances = rq1_results[i][0][6][0]
		cc_accuracy = rq1_results[i][0][6][1]
		cc_precision = rq1_results[i][0][6][2]
		cc_recall = rq1_results[i][0][6][3]
		cc_f1 = rq1_results[i][0][6][4]
		if cc_instances > 0:
			app_with_cc_instances += 1

		ca_instances = rq1_results[i][0][7][0]
		ca_accuracy = rq1_results[i][0][7][1]
		ca_precision = rq1_results[i][0][7][2]
		ca_recall = rq1_results[i][0][7][3]
		ca_f1 = rq1_results[i][0][7][4]
		if ca_instances > 0:
			app_with_ca_instances += 1

		cr_instances = rq1_results[i][0][8][0]
		cr_accuracy = rq1_results[i][0][8][1]
		cr_precision = rq1_results[i][0][8][2]
		cr_recall = rq1_results[i][0][8][3]
		cr_f1 = rq1_results[i][0][8][4]
		if cr_instances > 0:
			app_with_cr_instances += 1

		ic_instances = rq1_results[i][0][9][0]
		ic_accuracy = rq1_results[i][0][9][1]
		ic_precision = rq1_results[i][0][9][2]
		ic_recall = rq1_results[i][0][9][3]
		ic_f1 = rq1_results[i][0][9][4]
		if ic_instances > 0:
			app_with_ic_instances += 1


		#numerators for calculating overall average
		if tc_instances != 0:
			summed_tc_accuracy += tc_accuracy
			summed_tc_precision += tc_precision
			summed_tc_recall += tc_recall
			summed_tc_f1 += tc_f1
		if txc_instances != 0:
			summed_txc_accuracy += txc_accuracy
			summed_txc_precision += txc_precision
			summed_txc_recall += txc_recall
			summed_txc_f1 += txc_f1
		if ht_instances != 0:
			summed_ht_accuracy += ht_accuracy
			summed_ht_precision += ht_precision
			summed_ht_recall += ht_recall
			summed_ht_f1 += ht_f1
		if hs_instances != 0:
			summed_hs_accuracy +=  hs_accuracy
			summed_hs_precision +=  hs_precision
			summed_hs_recall +=  hs_recall
			summed_hs_f1 += hs_f1
		if vt_instances != 0:
			summed_vt_accuracy += vt_accuracy
			summed_vt_precision += vt_precision
			summed_vt_recall += vt_recall
			summed_vt_f1 += vt_f1
		if vs_instances != 0:
			summed_vs_accuracy +=  vs_accuracy
			summed_vs_precision += vs_precision
			summed_vs_recall += vs_recall
			summed_vs_f1 +=  vs_f1
		if cc_instances != 0:
			summed_cc_accuracy +=  cc_accuracy
			summed_cc_precision += cc_precision
			summed_cc_recall += cc_recall
			summed_cc_f1 += cc_f1
		if ca_instances != 0:
			summed_ca_accuracy += ca_accuracy
			summed_ca_precision += ca_precision
			summed_ca_recall += ca_recall
			summed_ca_f1 +=  ca_f1
		if cr_instances != 0:
			summed_cr_accuracy +=  cr_accuracy
			summed_cr_precision += cr_precision
			summed_cr_recall +=  cr_recall
			summed_cr_f1 += cr_f1
		if ic_instances != 0:
			summed_ic_accuracy +=  ic_accuracy
			summed_ic_precision += ic_precision
			summed_ic_recall +=  ic_recall
			summed_ic_f1 += ic_f1		
		

		#denominators for calculating overall average
		total_tc_instances += tc_instances
		total_txc_instances += txc_instances
		total_ht_instances += ht_instances
		total_hs_instances += hs_instances
		total_vt_instances += vt_instances
		total_vs_instances += vs_instances
		total_cc_instances += cc_instances
		total_ca_instances += ca_instances
		total_cr_instances += cr_instances
		total_ic_instances += ic_instances

		accuracy += rq1_results[i][1][0]
		precision += rq1_results[i][1][1]
		recall += rq1_results[i][1][2]
		f1_score += rq1_results[i][1][3]

	#typewise overall average
	print("Typewise performance with total instances:",'\n')
	if total_tc_instances!=0:
		overall_tc_accuracy = summed_tc_accuracy/app_with_tc_instances
		overall_tc_precision = summed_tc_precision/app_with_tc_instances
		overall_tc_recall = summed_tc_recall/app_with_tc_instances
		overall_tc_f1 = summed_tc_f1/app_with_tc_instances
		print("TC: ",total_tc_instances,"instances",overall_tc_accuracy, overall_tc_precision, overall_tc_recall, overall_tc_f1)

	if total_txc_instances!=0:
		overall_txc_accuracy = summed_txc_accuracy/app_with_txc_instances
		overall_txc_precision = summed_txc_precision/app_with_txc_instances
		overall_txc_recall = summed_txc_recall/app_with_txc_instances
		overall_txc_f1 = summed_txc_f1/app_with_txc_instances
		print("TXC: ",total_txc_instances,"instances",overall_txc_accuracy, overall_txc_precision, overall_txc_recall, overall_txc_f1)
	else:
		overall_txc_accuracy = 0
		overall_txc_precision = 0
		overall_txc_recall = 0
		overall_txc_f1 = 0

	if total_ht_instances!=0:
		overall_ht_accuracy = summed_ht_accuracy/app_with_ht_instances
		overall_ht_precision = summed_ht_precision/app_with_ht_instances
		overall_ht_recall = summed_ht_recall/app_with_ht_instances
		overall_ht_f1 = summed_ht_f1/app_with_ht_instances
		print("HT: ",total_ht_instances,"instances",overall_ht_accuracy, overall_ht_precision, overall_ht_recall, overall_ht_f1)
	else:
		overall_ht_accuracy = 0
		overall_ht_precision = 0
		overall_ht_recall = 0
		overall_ht_f1 = 0

	if total_hs_instances!=0:
		overall_hs_accuracy = summed_hs_accuracy/app_with_hs_instances
		overall_hs_precision = summed_hs_precision/app_with_hs_instances
		overall_hs_recall = summed_hs_recall/app_with_hs_instances
		overall_hs_f1 = summed_hs_f1/app_with_hs_instances
		print("HS: ",total_hs_instances,"instances",overall_hs_accuracy, overall_hs_precision, overall_hs_recall, overall_hs_f1)

	if total_vt_instances!=0:
		overall_vt_accuracy = summed_vt_accuracy/app_with_vt_instances
		overall_vt_precision = summed_vt_precision/app_with_vt_instances
		overall_vt_recall = summed_vt_recall/app_with_vt_instances
		overall_vt_f1 = summed_vt_f1/app_with_vt_instances
		print("VT: ",total_vt_instances,"instances",overall_vt_accuracy, overall_vt_precision, overall_vt_recall, overall_vt_f1)

	if total_vs_instances!=0:
		overall_vs_accuracy = summed_vs_accuracy/app_with_vs_instances
		overall_vs_precision = summed_vs_precision/app_with_vs_instances
		overall_vs_recall = summed_vs_recall/app_with_vs_instances
		overall_vs_f1 = summed_vs_f1/app_with_vs_instances
		print("VS: ",total_vs_instances,"instances",overall_vs_accuracy, overall_vs_precision, overall_vs_recall, overall_vs_f1)

	if total_cc_instances!=0:
		overall_cc_accuracy = summed_cc_accuracy/app_with_cc_instances
		overall_cc_precision = summed_cc_precision/app_with_cc_instances
		overall_cc_recall = summed_cc_recall/app_with_cc_instances
		overall_cc_f1 = summed_cc_f1/app_with_cc_instances
		print("CC: ",total_cc_instances,"instances",overall_cc_accuracy, overall_cc_precision, overall_cc_recall, overall_cc_f1)

	if total_ca_instances!=0:
		overall_ca_accuracy = summed_ca_accuracy/app_with_ca_instances
		overall_ca_precision = summed_ca_precision/app_with_ca_instances
		overall_ca_recall = summed_ca_recall/app_with_ca_instances
		overall_ca_f1 = summed_ca_f1/app_with_ca_instances
		print("CA: ",total_ca_instances,"instances",overall_ca_accuracy, overall_ca_precision, overall_ca_recall, overall_ca_f1)

	if total_cr_instances!=0:
		overall_cr_accuracy = summed_cr_accuracy/app_with_cr_instances
		overall_cr_precision = summed_cr_precision/app_with_cr_instances
		overall_cr_recall = summed_cr_recall/app_with_cr_instances
		overall_cr_f1 = summed_cr_f1/app_with_cr_instances
		print("CR: ",total_cr_instances,"instances",overall_cr_accuracy, overall_cr_precision, overall_cr_recall, overall_cr_f1)

	if total_ic_instances!=0:
		overall_ic_accuracy = summed_ic_accuracy/app_with_ic_instances
		overall_ic_precision = summed_ic_precision/app_with_ic_instances
		overall_ic_recall = summed_ic_recall/app_with_ic_instances
		overall_ic_f1 = summed_ic_f1/app_with_ic_instances
		print("IC: ",total_ic_instances,"instances",overall_ic_accuracy, overall_ic_precision, overall_ic_recall, overall_ic_f1)


	#typewise overall GuiEvo Perfomance
	typewise_overall_accuracy = (overall_tc_accuracy + overall_txc_accuracy + overall_ht_accuracy + 
						overall_hs_accuracy + overall_vt_accuracy + overall_vs_accuracy +
						overall_cc_accuracy + overall_ca_accuracy + overall_cr_accuracy + 
						overall_ic_accuracy)/ 10
	typewise_overall_precision = (overall_tc_precision + overall_txc_precision + overall_ht_precision + 
						overall_hs_precision + overall_vt_precision + overall_vs_precision +
						overall_cc_precision + overall_ca_precision + overall_cr_precision + 
						overall_ic_precision)/10
	typewise_overall_recall = (overall_tc_recall + overall_txc_recall + overall_ht_recall + 
						overall_hs_recall + overall_vt_recall + overall_vs_recall +
						overall_cc_recall + overall_ca_recall + overall_cr_recall + 
						overall_ic_recall)/10
	typewise_overall_f1 = (overall_tc_f1 + overall_txc_f1 + overall_ht_f1 + 
						overall_hs_f1 + overall_vt_f1 + overall_vs_f1 +
						overall_cc_f1 + overall_ca_f1 + overall_cr_f1 + 
						overall_ic_f1)/10

	#app-wise overall GuiEvo Perfomance
	appwise_overall_accuracy = accuracy/total_apps
	appwise_overall_precision = precision/total_apps
	appwise_overall_recall = recall/total_apps
	appwise_overall_f1 = f1_score/total_apps

	return typewise_overall_accuracy, typewise_overall_precision, typewise_overall_recall, typewise_overall_f1, appwise_overall_accuracy, appwise_overall_precision, appwise_overall_recall, appwise_overall_f1


def flatten(change_types):
	flatlist = []
	for change_list in change_types:
		change_list = change_list.replace('"','').replace("'","").replace('[','').replace(']','').replace(' ','').split(',')
		flatlist.append(change_list)
	flatlist = [ct for sublist in flatlist for ct in sublist]
	return flatlist



def compile_tool_result(root_directory,tv):
	#dataframe containing information on removed components
	df1 = pd.read_csv(root_directory+"/["+str(tv)+']_basic_info.csv')
	df1 = df1[df1['change_types'] == "['CR']"]
	df1 = df1[['old_bounds','new_bounds','node_attributes','new_attributes','change_types','class']]
	#dataframe containing information on added and modified components
	df2 = pd.read_csv(root_directory+"/["+str(tv)+']_dynamic_xml_base.csv')
	#df2 = df2.loc[df2['change_types'] != 'NC']
	df2 = df2[df2['change_types'].notna()]	
	df2 = df2[['old_bounds','new_bounds','node_attributes','new_attributes','change_types','class']]
	#combined dataframe with all changes
	df = pd.concat([df1, df2])
	df.reset_index(drop=True, inplace=True)
	df.to_csv(root_directory+"/"+"["+str(tv)+"]_tool_output.csv", index=False)
	return df


def get_rq1_result(conf_matrix):
	#print(conf_matrix)
	#print()
	
	change_types = ['TC','TXC','HT','HS','VT','VS','CC','CA','CR','IC']
	accuracy_numerator,precision_numerator,recall_numerator,f1_numerator,denominator = 0,0,0,0,0
	change_wise_result = []
	for ct in change_types:
		if conf_matrix[ct][0] != 0:
			accuracy_numerator += conf_matrix[ct][1][0]
			precision_numerator += conf_matrix[ct][1][1]
			recall_numerator += conf_matrix[ct][1][2]
			f1_numerator += conf_matrix[ct][1][3]
			denominator += 1
			result = (conf_matrix[ct][0],conf_matrix[ct][1][0], conf_matrix[ct][1][1], conf_matrix[ct][1][2], conf_matrix[ct][1][3])
		else:
			result = (0,None, None, None, None)
		change_wise_result.append(result)
		print(ct,result)
		
	average_accuracy = accuracy_numerator/denominator
	average_precision = precision_numerator/denominator
	average_recall = recall_numerator/denominator
	average_f1 = f1_numerator/denominator

	print("Accuracy: ",average_accuracy,"Precision:", average_precision,"Recall:",average_recall,"F1-Score:",average_f1)
	return change_wise_result, (average_accuracy,average_precision,average_recall,average_f1)


def get_record(tp,fp,fn,tn):
	#print(tp,fp,fn,tn)
	if tp == 0 and fp == 0 and fn == 0 and tn == 0:
		return (0,0,0,0)
	else:
		accuracy = (tp+tn)/(tp+fp+fn+tn)

		if tp == 0 and fp == 0 and fn == 0:
			precision = 1
			recall = 1
		elif tp == 0:
			precision = 0
			recall = 0
		else:
			precision = tp / (tp + fp)
			recall = tp / (tp + fn)
		
		if precision == 0 or recall == 0:
			f1_score = 0
		else:
			f1_score = (2 * precision * recall) / (precision + recall)
		
		record = (round(accuracy,2),round(precision,2),round(recall,2),round(f1_score,2))
		return record



def get_confusion_matrix(tool_info,gt_info,root_directory):
	tc_tp, tc_fp, tc_fn, tc_tn = 0,0,0,0
	txc_tp, txc_fp, txc_fn, txc_tn = 0,0,0,0
	ht_tp, ht_fp, ht_fn, ht_tn = 0,0,0,0
	hs_tp, hs_fp, hs_fn, hs_tn = 0,0,0,0
	vt_tp, vt_fp, vt_fn, vt_tn = 0,0,0,0
	vs_tp, vs_fp, vs_fn, vs_tn = 0,0,0,0
	cc_tp, cc_fp, cc_fn, cc_tn = 0,0,0,0
	ca_tp, ca_fp, ca_fn, ca_tn = 0,0,0,0
	cr_tp, cr_fp, cr_fn, cr_tn = 0,0,0,0
	ic_tp, ic_fp, ic_fn, ic_tn = 0,0,0,0

	change_wise_cf_info = {}
	change_types = ['TC','TXC','HT','VT','HS','VS','CC','CA','CR','IC']
	gt_node_wise_single_change_list = []
	gt_bounds_list =  []
	gt_old_attribute_list = []
	gt_change_list = []
	for i in range(len(gt_info)):
		changes = gt_info.loc[i,'change_types']
		changes = [ele for ele in change_types if(ele in changes)]
		gt_change_list.append(changes)
		for j in changes:
			if j == 'CA':
				text = gt_info.loc[i,'new_attributes'].split("'text':")[1].split("'resource-id'")[0].split(".")[-1].strip(" ")
			else:
				text = gt_info.iloc[i]['node_attributes'].split("'text':")[1].split("'resource-id'")[0].split(".")[-1].strip(" ")
			tuple_i = (j,gt_info.loc[i,'old_bounds'], gt_info.loc[i,'new_bounds'], gt_info.loc[i,'node_attributes'], gt_info.loc[i,'new_attributes'],gt_info.loc[i,'class'],text)
			gt_node_wise_single_change_list.append(tuple_i)
		gt_old_attribute_list.append(gt_info.loc[i,'node_attributes'])
		gt_bounds_list.append(gt_info.loc[i,'old_bounds'])
	gt_change_list = [sublist for sublist in gt_change_list if sublist]
	gt_change_list = [element for sublist in gt_change_list for element in sublist]

	tool_indices = list(tool_info.index.values)
	tool_node_wise_single_change_list = []
	tool_bounds_list =  []
	tool_change_list = []
	tool_old_attribute_list = []
	for i in tool_indices:
		changes = tool_info.loc[i,'change_types']
		changes = [ele for ele in change_types if(ele in changes)]
		tool_change_list.append(changes)
		#print(changes)
		for j in changes:
			if j == 'CA':
				text = tool_info.loc[i,'new_attributes'].split("'text':")[1].split("'resource-id'")[0].split(".")[-1].strip(" ")
			else:
				text = tool_info.loc[i,'node_attributes'].split("'text':")[1].split("'resource-id'")[0].split(".")[-1].strip(" ")
			tuple_i = (j,tool_info.loc[i,'old_bounds'], tool_info.loc[i,'new_bounds'], tool_info.loc[i,'node_attributes'], tool_info.loc[i,'new_attributes'],tool_info.loc[i,'class'],text)
			tool_node_wise_single_change_list.append(tuple_i)
			
		tool_old_attribute_list.append(tool_info.loc[i,'node_attributes'])
		tool_bounds_list.append(tool_info.loc[i,'old_bounds'])

	tool_change_list = [sublist for sublist in tool_change_list if sublist]
	tool_change_list = [element for sublist in tool_change_list for element in sublist]
	
	for gt_tuple in gt_node_wise_single_change_list:
		if gt_tuple[0] == 'CA':
			if 'CA' in tool_change_list:
				flag = False
				for tool_tuple in tool_node_wise_single_change_list:
					if tool_tuple[0]=='CA' and gt_tuple[5] == tool_tuple[5] and gt_tuple[6] == tool_tuple[6]:
						ca_tp += 1
						flag = True
				if not flag:
					ca_tp += 0.5
			else:
				ca_fn += 1
		else:
			if gt_tuple[3] in tool_old_attribute_list:
				if gt_tuple[0] == 'TC':
					tc_tp += 1
				if gt_tuple[0] == 'TXC':
					txc_tp += 1
				if gt_tuple[0] == 'HT':
					ht_tp += 1
				if gt_tuple[0] == 'HS':
					hs_tp += 1
				if gt_tuple[0] == 'VT':
					vt_tp += 1
				if gt_tuple[0] == 'VS':
					vs_tp += 1	
				if gt_tuple[0] == 'CC':
					cc_tp += 1
				if gt_tuple[0] == 'CR':
					cr_tp += 1
				if gt_tuple[0] == 'IC':
					ic_tp += 1
			else:
				if gt_tuple[0] == 'TC':
					tc_fn += 1
				if gt_tuple[0] == 'TXC':
					txc_fn += 1
				if gt_tuple[0] == 'HT':
					ht_fn += 1
				if gt_tuple[0] == 'HS':
					hs_fn += 1
				if gt_tuple[0] == 'VT':
					vt_fn += 1
				if gt_tuple[0] == 'VS':
					vs_fn += 1	
				if gt_tuple[0] == 'CC':
					cc_fn += 1
				if gt_tuple[0] == 'CR':
					cr_fn += 1
				if gt_tuple[0] == 'IC':
					new_tup = ('CR',gt_tuple[1],gt_tuple[2],gt_tuple[3],gt_tuple[4],gt_tuple[5],gt_tuple[6])
					if new_tup in tool_node_wise_single_change_list:
						ic_tp += 1
					else:
						ic_fn += 1

	for tool_tuple in tool_node_wise_single_change_list:
		if tool_tuple[0] == 'CA':
			if tool_tuple[0] not in gt_change_list:
				ca_fp += 1
			elif tool_tuple[0] in gt_change_list:
				flag = False
				for gt_tuple in gt_node_wise_single_change_list:
					if gt_tuple[0]=='CA' and gt_tuple[5] == tool_tuple[5] and gt_tuple[6] == tool_tuple[6]:
						flag = True
				if not flag:
					ca_fp += 0.5
		else:
			if tool_tuple[3] not in gt_old_attribute_list:
				if tool_tuple[0] == 'TC':
					tc_fp += 1
				if tool_tuple[0] == 'TXC':
					txc_fp += 1
				if tool_tuple[0] == 'HT':
					ht_fp += 1
				if tool_tuple[0] == 'HS':
					hs_fp += 1
				if tool_tuple[0] == 'VT':
					vt_fp += 1
				if tool_tuple[0] == 'VS':
					vs_fp += 1	
				if tool_tuple[0] == 'CC':
					cc_fp += 1
				if tool_tuple[0] == 'CR':
					cr_fp += 1
				if tool_tuple[0] == 'IC':
					ic_fp += 1
	
	tool_node_wise_single_change_list = []
	all_change_types = ['NC']
	for i in tool_indices:
		changes = tool_info.loc[i,'change_types']
		changes = [ele for ele in all_change_types if(ele in changes)]
		for j in changes:
			#tuple_i = (j,tool_info.loc[i,'class'],tool_info.loc[i,'old_bounds'],tool_info.loc[i,'node_attributes'])
			tuple_i = (j,tool_info.loc[i,'old_bounds'], tool_info.loc[i,'new_bounds'], tool_info.loc[i,'node_attributes'], tool_info.loc[i,'new_attributes'],tool_info.loc[i,'class'],text)
			tool_node_wise_single_change_list.append(tuple_i)
	for tuple_i in tool_node_wise_single_change_list:
		if tuple_i not in gt_node_wise_single_change_list:
			if tuple_i[0] == 'TC':
				tc_tn += 1
			if tuple_i[0] == 'TXC':
				txc_tn += 1
			if tuple_i[0] == 'HT':
				ht_tn += 1
			if tuple_i[0] == 'HS':
				hs_tn += 1
			if tuple_i[0] == 'VT':
				vt_tn += 1
			if tuple_i[0] == 'VS':
				vs_tn += 1	
			if tuple_i[0] == 'CC':
				cc_tn += 1
			if tuple_i[0] == 'CA':
				ca_tn += 1
			if tuple_i[0] == 'CR':
				cr_tn += 1
			if tuple_i[0] == 'IC':
				ic_tn += 1

	tc_instances = tc_tp + tc_fp + tc_tn + tc_fn
	txc_instances = txc_tp + txc_fp + txc_tn + txc_fn
	ht_instances = ht_tp + ht_fp + ht_tn + ht_fn
	hs_instances = hs_tp + hs_fp + hs_tn + hs_fn
	vt_instances = vt_tp + vt_fp + vt_tn + vt_fn
	vs_instances = vs_tp + vs_fp + vs_tn + vs_fn
	cc_instances = cc_tp + cc_fp + cc_tn + cc_fn
	ca_instances = ca_tp + ca_fp + ca_tn + ca_fn
	cr_instances = cr_tp + cr_fp + cr_tn + cr_fn
	ic_instances = ic_tp + ic_fp + ic_tn + ic_fn

	change_wise_cf_info['TC'] = (tc_instances,get_record(tc_tp,tc_fp,tc_fn,tc_tn))
	change_wise_cf_info['TXC'] = (txc_instances, get_record(txc_tp,txc_fp,txc_fn,txc_tn))
	change_wise_cf_info['HT'] = (ht_instances, get_record(ht_tp,ht_fp,ht_fn,ht_tn))
	change_wise_cf_info['HS'] = (hs_instances, get_record(hs_tp,hs_fp,hs_fn,hs_tn))
	change_wise_cf_info['VT'] = (vt_instances, get_record(vt_tp,vt_fp,vt_fn,vt_tn))
	change_wise_cf_info['VS'] = (vs_instances, get_record(vs_tp,vs_fp,vs_fn,vs_tn))
	change_wise_cf_info['CC'] = (cc_instances, get_record(cc_tp,cc_fp,cc_fn,cc_tn))
	change_wise_cf_info['CA'] = (ca_instances, get_record(ca_tp,ca_fp,ca_fn,ca_tn))
	change_wise_cf_info['CR'] = (cr_instances, get_record(cr_tp,cr_fp,cr_fn,cr_tn))
	change_wise_cf_info['IC'] = (ic_instances, get_record(ic_tp,ic_fp,ic_fn,ic_tn))

	#print(change_wise_cf_info['CR'][1])
	change_wise_result, rq1_result = get_rq1_result(change_wise_cf_info) #returned: (change_wise_result,average_accuracy,average_precision,average_recall,average_f1)
	return change_wise_result, rq1_result


