import csv
import pandas as pd
import numpy as np
import os
import shutil 

unavailable_GPlay = ["Unavailable"]

#Removing APK from the list for which no GooglePlayLink was available
df = pd.read_csv("F-Droid App Info.csv")
df = df[~df['GooglePlayLink'].isin(unavailable_GPlay)]

#Removing APK from the list for which there are <1000 downloads
df['Downloads'] = df['Downloads'].str.replace(r'\D', "", regex=True)
df['Downloads'] = pd.to_numeric(df['Downloads'])
df['Downloads'] = df['Downloads'].replace(np.nan, -1, regex=True)
df = df[(df['Downloads'] >= 1000)]

#writing the filtered app info to .csv file
#df.to_csv(r'Filtered APK List.csv', index = False)

#moving app folders to mark as filtered
source = "/Users/sabihasalma/Documents/Academic/Research/Summer Project 2021/APK/"
destination = "/Users/sabihasalma/Documents/Academic/Research/Summer Project 2021/Filtered APK/"
for app in df['Package']:
    shutil.move(source+app, destination)
