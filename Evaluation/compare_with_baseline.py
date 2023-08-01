from config import *
import os
import glob
from skimage.metrics import structural_similarity as ssim
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_squared_error as mse
import Evaluation.ted as ted 
import cv2


def calculate_mse(new_img, generated_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(generated_img)
	nsamples, nx, ny = im1.shape
	im1 = im1.reshape((nsamples,nx*ny))
	nsamples, nx, ny = im2.shape
	im2 = im2.reshape((nsamples,nx*ny))
	sq_err = mse(im1, im2)
	return sq_err



def calculate_mae(new_img, generated_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(generated_img)
	nsamples, nx, ny = im1.shape
	im1 = im1.reshape((nsamples,nx*ny))
	nsamples, nx, ny = im2.shape
	im2 = im2.reshape((nsamples,nx*ny))
	abs_err = mae(im1,im2)
	return abs_err



def calculate_ssim(new_img, generated_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(generated_img)
	im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
	im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
	sim = ssim(im1_gray, im2_gray, channel_axis=None)
	return sim



def calculate_xml_difference(new_xml, generated_xml):
	distance = ted.get_ted(new_xml,generated_xml)
	return distance



def compare_XMLs(guievo_path, remaui_path, redraw_path):
	print('\n\n')
	ted_guievo, ted_remaui, ted_redraw = [],[],[]

	for app in recompiled_apps:
		remaui_xml = remaui_path+app+'/'+'remaui_xml.xml'
		redraw_xml = redraw_path+app+'/'+'redraw_xml.xml'
		guievo_recompiled_xml = guievo_path+app+'/'+'recompiled_xml.xml'
		new_xml = remaui_path+app+'/'+'new_xml.xml'
		
		ted_guievo_result = calculate_xml_difference(new_xml,guievo_recompiled_xml)
		ted_remaui_result = calculate_xml_difference(new_xml,remaui_xml)
		ted_redraw_result = calculate_xml_difference(new_xml,redraw_xml)
		
		ted_guievo.append(ted_guievo_result)
		ted_remaui.append(ted_remaui_result)
		ted_redraw.append(ted_redraw_result)

		print(app,":\nTED	[GuiEvo: ",ted_guievo_result,", REMAUI: ",ted_remaui_result,", ReDraw: ",ted_redraw_result,"]\n")

	print("Average tree edit distance: GuiEvo [", sum(ted_guievo)/len(recompiled_apps),"]	REMAUI [",sum(ted_remaui)/len(recompiled_apps),"]	ReDraw [",sum(ted_redraw)/len(recompiled_apps),"]")


	
def compare_screens(guievo_path, remaui_path):
	ssim_remaui, ssim_guievo = [],[]
	mae_remaui, mae_guievo = [],[]
	mse_remaui, mse_guievo = [],[]
	print('\n\n')
	for app in recompiled_apps:

		remaui_screen = remaui_path+app+'/'+'remaui_ss.png'
		guievo_recompiled_screen = guievo_path+app+'/'+'recompiled_ss.png'
		new_screen = remaui_path+app+'/'+'new_ss.png'
		
		ssim_remaui_result = calculate_ssim(new_screen,remaui_screen)
		mae_remaui_result = calculate_mae(new_screen,remaui_screen)
		mse_remaui_result = calculate_mse(new_screen,remaui_screen)
		ssim_remaui.append(ssim_remaui_result)
		mae_remaui.append(mae_remaui_result)
		mse_remaui.append(mse_remaui_result)
		
		ssim_guievo_result = calculate_ssim(new_screen,guievo_recompiled_screen)
		mae_guievo_result = calculate_mae(new_screen,guievo_recompiled_screen)
		mse_guievo_result = calculate_mse(new_screen,guievo_recompiled_screen)
		ssim_guievo.append(ssim_guievo_result)
		mae_guievo.append(mae_guievo_result)
		mse_guievo.append(mse_guievo_result)
		
		print(app,":\nSSIM[GuiEvo: ",ssim_guievo_result,", REMAUI: ",ssim_remaui_result,"]\nMAE[GuiEvo: ",mae_guievo_result,", REMAUI: ",mae_remaui_result,"]\nMSE[GuiEvo: ",mse_guievo_result,", REMAUI: ",mse_remaui_result,"]\n")


	print("Average image similarity: GuiEvo [", sum(ssim_guievo)/len(recompiled_apps),"]	REMAUI [",sum(ssim_remaui)/len(recompiled_apps),"]")
	print("Average mae: GuiEvo [", sum(mae_guievo)/len(recompiled_apps),"]	REMAUI [",sum(mae_remaui)/len(recompiled_apps),"]")
	print("Average mse: GuiEvo [", sum(mse_guievo)/len(recompiled_apps),"]	REMAUI [",sum(mse_remaui)/len(recompiled_apps),"]")
	

