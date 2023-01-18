from bs4 import BeautifulSoup
import requests
import re
import warnings
import os
import pandas as pd


warnings. filterwarnings("ignore")

baseUrl = "https://github.com"
filepath = "./Downloads/"
appDict = {}

"""
appName = "at.jclehner.rxdroid"
appUrl = "https://github.com/jclehner/rxdroid/"
apkUrl = appUrl+"releases"

directory = filepath+appName
path = os.path.join(filepath, appName)
if not os.path.exists(directory):
    os.mkdir(path)

html_page = requests.get(apkUrl,verify=False).text
soup = BeautifulSoup(html_page, "lxml")
links = soup.findAll('a')

if len(links) > 0:
    for link in links:
        if ".apk" in str(link):
            apkLink = baseUrl+link.get('href')
            req = requests.get(apkLink, verify=False)
            fileName = re.findall(r"[^/\\&\?]+\.\w{3,4}",apkLink)[1]
            with open(directory+"/"+fileName, 'wb') as f:
                f.write(req.content)
            print(fileName,"Downloaded")
else:
    print("No links found")
"""

def downloadReleases(appName,fileName,versionNum,req):
    basedirectory = filepath+appName
    basepath = os.path.join(filepath, appName)
    if not os.path.exists(basedirectory):
        os.mkdir(basepath)
    apkdirectory = basedirectory+'/'+versionNum
    apkpath = os.path.join(basedirectory, versionNum)
    if not os.path.exists(apkdirectory):
        os.mkdir(apkpath)
    fileName = appName+'_'+versionNum+"_"+fileName
    with open(apkdirectory+"/"+fileName, 'wb') as f:
        f.write(req.content)
        print(appName,'Version',versionNum,'downloaded')


def getReleases(appName,links):
    count = 0
    for link in links:
        if ".apk" in str(link):
            apkLink = baseUrl+link.get('href')
            req = requests.get(apkLink, verify=False)
            urlSeg = apkLink.split('/')
            versionNum = urlSeg[len(urlSeg)-2]
            try:
                versionNum = re.findall(r"^[^0-9]*(([0-9]+\.)*[0-9]+).*",versionNum)[0][0]
            except:
                versionNum = 'NONE'
            fileName = urlSeg[len(urlSeg)-1]
            downloadReleases(appName,fileName,versionNum,req)
            count+=1
    print(appName,":",count,"releases downloaded")


def getApkLinks(appName, appUrl):
    apkUrl = appUrl+"/releases"
    html_page = requests.get(apkUrl,verify=False).text
    soup = BeautifulSoup(html_page, "lxml")
    links = soup.findAll('a')
    if len(links) > 0:
        getReleases(appName,links)
    else:
        print("No links found")


def fetchApkInfo():
    df = pd.read_csv("Filtered APK List.csv")
    appNames = df.loc[:, ['Package']].values
    appUrls = df.loc[:, ['SourceCode']].values
    for app in range (0,len(appNames)):
        appName = appNames[app][0]
        appUrl = appUrls[app][0]
        getApkLinks(appName, appUrl)


if __name__ == "__main__":
    fetchApkInfo()
