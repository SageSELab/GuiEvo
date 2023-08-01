root = "/Users/sabihasalma/Documents/Academic/Research/ICSE24-GuiEvo/"
evaluation_data_directory = root + "Evaluation-Dataset/"
Modelcheckpoint = root + 'Detection/modelDir_frozen_inception_v3.pb'
label_filepath = root + 'Detection/labels.txt'
metadata = root + "Metadata/"
evaluation = root + "Evaluation/"
ReDraw = evaluation + "Comparison-with-ReDraw/"
REMAUI = evaluation + "Comparison-with-REMAUI/"
GuiEvo = evaluation + "Comparison-with-GuiEvo/"
total_apps = 22
api_key = 'AIzaSyA-ujCcMcf9lFyYayl5XKMnRVrxOx651_U'


app_versions = [
	"amirz.rootless.nexuslauncher/3.9-vs-3.9.1",
	"app.olauncher/2.1-vs-2.4",
	"app.zeusln.zeus/0.3.1-vs-0.4.0",
	"apps.jizzu.simpletodo/1.5-vs-1.6",
	"at.jclehner.rxdroid/0.9.33.1-vs-0.9.33.2",
	"be.mygod.vpnhotspot/2.12.2-vs-2.12.3",
	"ca.mimic.apphangar/2.0-vs-2.1.1",
	"chat.rocket.android/4.14.1-vs-4.15.0",
	"ch.rmy.android.http_shortcuts/1.39.0-vs-2.0.0",
	"com.adam.aslfms/1.6.7-vs-1.6.9",
	"com.emanuelef.remote_capture/1.3.6-vs-1.3.7",
	"com.emmanuelmess.simpleaccounting/1.5.1.1-vs-1.5.2",	
	"com.ensoft.imgurviewer/2.1.8-vs-2.1.9",
	"com.finnmglas.launcher/1.5.0-vs-1.6.0",
	"com.gianlu.aria2android/2.4.2-vs-2.4.3",
	"ch.rmy.android.statusbar_tacho/1.2-vs-2.0",
	"com.gimranov.zandy/1.4.2-vs-1.4.5",
	"com.github.gotify/2.0.14-vs-2.1.0",
	"com.readrops/1.0.2.2-vs-1.1.0",
	"com.rohitsuratekar.NCBSinfo/6.6.7-vs-6.6.9",
	"com.secuso.torchlight2/1.2-vs-1.3",
	"xyz.zedler.patrick.grocy/1.8.3-vs-1.8.4",
	
]	

threshold_values = {
	'amirz.rootless.nexuslauncher':0.95,
	'app.olauncher':0.7,
	'app.zeusln.zeus':0.7,
	'apps.jizzu.simpletodo':0.95,
	'at.jclehner.rxdroid':0.7,
	'be.mygod.vpnhotspot':0.95,
	'ca.mimic.apphangar':0.95,
	'chat.rocket.android':0.7,
	'ch.rmy.android.http_shortcuts':0.95,
	'com.adam.aslfms':0.7,
	'com.emanuelef.remote_capture':0.7,
	'com.emmanuelmess.simpleaccounting':0.95,
	'com.ensoft.imgurviewer':0.95,
	'com.finnmglas.launcher':0.7,
	'com.gianlu.aria2android':0.85,
	'ch.rmy.android.statusbar_tacho':0.85,
	'com.gimranov.zandy':0.7,
	'com.github.gotify':0.7,
	'com.readrops':0.7,
	'com.rohitsuratekar.NCBSinfo':0.85,
	'com.secuso.torchlight2':0.95,
	'xyz.zedler.patrick.grocy':0.7
}

recompiled_apps = [
	'xyz.zedler.patrick.grocy',
	'com.readrops',
	'com.finnmglas.launcher',
	'com.ensoft.imgurviewer',
	'at.jclehner.rxdroid',
	'app.olauncher'
]

inputs = [
	"old_ss.png",
	"old_xml.xml",
	"new_ss.png",
	"new_xml.xml",
]

tool_csv_header = [
	'node_num',
	'xml_level',
	'xml_index',
	'parent_location',
	'parent_node_num',
	'isParent',
	'node_attributes',
	'component_validity',
	'old_bounds',
	'new_bounds',
	'total_changes',
	'change_types',
	'new_attributes',
	'class'
	]


gt_header = [
	'old_bounds',
	'new_bounds',
	'node_attributes',
	'new_attributes',
	'change_types',
	'class'
	]

apps_header = [
	'App',
	'SSIM',
	'MSE',
	'PSNR',
	'NCC',
	'SC',
	'Best Threshold'
	]