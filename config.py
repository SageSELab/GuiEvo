#Set True to run on sample data
sample_dataset = True
#Set app to 0 or 1 or 2 for trying three different samples
app = str(1)
#Directory path for sample data to be run. 
sample_data_directory = "/Users/sabihasalma/Documents/Academic/Research/ASE22/Datasets/Sample-Dataset/"+app+"/"


#Set True to run on evaluation dataset
evaluation_dataset = False
#Directory path for evaluation dataset to be run.
evaluation_data_directory = "/Users/sabihasalma/Documents/Academic/Research/ASE22/Datasets/Evaluation-Dataset/"

#sub_directories for holding cropped GUI components
dirs = {
    "old_comps": "oldGUI_directory",
    "mapped_comps": "mappedGUI_directory",
    "diff_comps": "diffGUI_directory",
}

csv_filename = "gui_changes.csv"
Modelcheckpoint = '/Users/sabihasalma/Documents/Academic/Research/ASE22/modelDir_frozen_inception_v3.pb'
label_filepath = '/Users/sabihasalma/Documents/Academic/Research/ASE22/labels.txt'    