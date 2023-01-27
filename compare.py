import os
import glob
from skimage.metrics import structural_similarity as ssim
from sklearn.metrics import mean_absolute_error as mae
from sklearn.metrics import mean_squared_error as mse
import TED_Calculation.ted as ted 
import cv2

root = "/Users/sabihasalma/Documents/Academic/Research/GUIEvo/Recompilation/GuiEvo-Screenshots/"


def calculate_mse(new_img, recompiled_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(recompiled_img)
	nsamples, nx, ny = im1.shape
	im1 = im1.reshape((nsamples,nx*ny))
	nsamples, nx, ny = im2.shape
	im2 = im2.reshape((nsamples,nx*ny))
	sq_err = mse(im1, im2)
	print("mean squared error:",sq_err)
	return sq_err



def calculate_mae(new_img, recompiled_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(recompiled_img)
	nsamples, nx, ny = im1.shape
	im1 = im1.reshape((nsamples,nx*ny))
	nsamples, nx, ny = im2.shape
	im2 = im2.reshape((nsamples,nx*ny))
	abs_err = mae(im1,im2)
	print("mean absolute error:",abs_err)
	return abs_err



def calculate_ssim(new_img, recompiled_img):
	im1 = cv2.imread(new_img)
	im2 = cv2.imread(recompiled_img)
	sim = ssim(im1,im2,full=True,channel_axis=2)[0]
	print("structural similarity:",sim)
	return sim


def calculate_xml_difference(new_xml, recompiled_xml):
	distance = ted.get_ted(new_xml,recompiled_xml)
	print("tree edit distance:",distance)
	return distance


if __name__ == '__main__':
	apps = glob.glob(root+'*', recursive = True)
	image_similarity = []
	mean_average_error = []
	mean_square_error = []
	tree_edit_distance = []
	for app in apps:
		print(app)
		files = []
		for it in os.scandir(app):
			files.append(it.path)
		for file in files:
			if file.endswith("new_ss.png"):
				new_png_path = file
			if file.endswith("recompiled_ss.png"):
				recompiled_png_path = file
			if file.endswith("new_xml.xml"):
				new_xml_path =file
			if file.endswith("recompiled_xml.xml"):
				recompiled_xml_path = file
		
		image_similarity.append(calculate_ssim(new_png_path,recompiled_png_path))
		mean_average_error.append(calculate_mae(new_png_path,recompiled_png_path))
		mean_square_error.append(calculate_mse(new_png_path,recompiled_png_path))
		tree_edit_distance.append(calculate_xml_difference(new_xml_path,recompiled_xml_path))
		print()
	print()
	print("=============================")
	print("Average image similarity: ", sum(image_similarity)/len(apps))
	print("Average mae: ", sum(mean_average_error)/len(apps))
	print("Average mse: ", sum(mean_square_error)/len(apps))
	print("Average tree edit distance: ", sum(tree_edit_distance)/len(apps))
	