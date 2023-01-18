import os
from itertools import compress
from distutils.version import StrictVersion
import re
import pathlib
import numpy as np
import subprocess

root = "/Users/user/Documents/Academic/Research/GuiEvo/"
gcat_resource_folder = root + "GCat-Input-Data/"
gcat_output_folder = root + "GCat-Output/"
	

def run_gcat(app, v1, v2, screens):
	path = gcat_resource_folder+app+"/"+v1+"-vs-"+v2+"/"+app+"_"
	for i in range(0,1):#range(len(screens)):
		if not os.path.exists(gcat_output_folder+app+"/"+v1+"-vs-"+v2+"/"+screens[i]):
			os.mkdir(os.path.join(gcat_output_folder+app+"/"+v1+"-vs-"+v2, screens[i]))

		ss1_path = os.path.abspath(path+v1+"_"+screens[i]+".png")
		ss2_path = os.path.abspath(path+v2+"_"+screens[i]+".png")
		xml1_path = os.path.abspath(path+v1+"_"+screens[i]+".xml")
		xml2_path = os.path.abspath(path+v2+"_"+screens[i]+".xml")
		
		print("java -jar GCat.jar",ss1_path, xml1_path, ss2_path, xml2_path)
		#subprocess.call(['java', '-jar', 'GCat.jar', ss1_path, xml1_path, ss2_path, xml2_path])


def get_screens():
	appNames = sorted(next(os.walk(gcat_resource_folder))[1])
	for app in appNames[2:3]:
		if not os.path.exists(gcat_output_folder+app):
			os.mkdir(os.path.join(gcat_output_folder, app))
		app_version_pairs = sorted(next(os.walk(gcat_resource_folder+"/"+app))[1])
		screenshot_paths = []
		xml_paths = []
		for pair in app_version_pairs[0:1]:
			if not os.path.exists(gcat_output_folder+app+"/"+pair):
				os.mkdir(os.path.join(gcat_output_folder+app+"/", pair))
			
			version1 = pair.split("-vs-")[0]
			version2 = pair.split("-vs-")[1]
			screens = []
			screenshots = sorted(list(pathlib.Path(gcat_resource_folder+app+"/"+pair+"/").glob('*.png')))
			xmls = sorted(list(pathlib.Path(gcat_resource_folder+app+"/"+pair+"/").glob('*.xml')))
			for sc in screenshots:
				screens.append(str(sc).replace('/','')[-6:].replace('.png','').replace('_',''))
			screens = list(np.unique(np.array(screens)))
			run_gcat(app,version1,version2,screens)


if __name__ == "__main__":
	get_screens()
