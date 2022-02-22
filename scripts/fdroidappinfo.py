import os
import re
import csv
from bs4 import BeautifulSoup
import requests
import play_scraper
import shutil

appNamesList = []
root = "$HOME/go/bin/fdroidcl"
apkRootDirectory = "/Users/sabihasalma/Documents/Academic/Research/Summer Project 2021/APK/"


def downloadApk():
    print("Downloading the .apk files")
    apps = appNamesList
    count = 1
    for app in apps:
        info = os.popen(root+" show "+app).read().split("\n")
        print("\n",count," - ",app)
        package,name,versions = getAppInfo(info,True)
        print(package,name,versions)

        directory = apkRootDirectory+app
        path = os.path.join(apkRootDirectory, app)
        if not os.path.exists(directory):
            os.mkdir(path)
        sourceDirectory = "/Users/sabihasalma/Library/Caches/fdroidcl/apks/"
        destDirectory = directory

        for version in versions:
            versionNum = re.search(r"\(([A-Za-z0-9_]+)\)", version).group(1)
            try:
                os.system(root+" download "+app+ ":" +versionNum)
                if not os.path.exists(destDirectory+"/"+app+"_"+versionNum):
                    shutil.move(sourceDirectory+app+"_"+versionNum+".apk", destDirectory+"/")
                else:
                    pass
            except:
                pass
        count += 1


def getGooglePlayInfo(package,sourceCode):
    try:
        html_page = requests.get(sourceCode).text
        print(html_page)
        soup = BeautifulSoup(html_page, "lxml")
        links = soup.findAll('a')
        if len(links) > 0:
            for link in links:
                if "play.google.com/store" in str(link):
                    details = play_scraper.details(package)
                    stars = details["score"]
                    downloads = details["installs"]
                    return link.get('href'),stars,downloads
            return "Unavailable","Unavailable","Unavailable"
        else:
            print("No links found")
            return "Unavailable","Unavailable","Unavailable"
    except:
        print("Bad HTML request")
        return "Unavailable","Unavailable","Unavailable"


def getAppInfo(info,download):
    package = name = summary = added = lastUpdated = currentVersion = license = category = website = sourceCode = issueTracker = changeLog = bitcoin = des = donate = ""
    for line in info:
        if line.startswith("Package  "):
            package = line.split(": ")[1]
        elif line.startswith("Name  "):
            name = line.split(": ")[1]
        elif line.startswith("Summary  "):
            summary = line.split(": ")[1]
        elif line.startswith("Added  "):
            added = line.split(": ")[1]
        elif line.startswith("Last Updated"):
            lastUpdated = line.split(": ")[1]
        elif line.startswith("Version  "):
            currentVersion = line.split(": ")[1]
        elif line.startswith("License  "):
            license = line.split(": ")[1]
        elif line.startswith("Categories  "):
            category = line.split(": ")[1]
        elif line.startswith("Website  "):
            website = line.split(": ")[1]
        elif line.startswith("Source Code  "):
            sourceCode = line.split(": ")[1]
        elif line.startswith("Issue Tracker"):
            issueTracker = line.split(": ")[1]
        elif line.startswith("Changelog  "):
            changeLog = line.split(": ")[1]
        elif line.startswith("Donate  "):
            donate = line.split(": ")[1]
        elif line.startswith("Bitcoin  "):
            bitcoin = line.split(": ")[1]
        elif line.startswith("Available Versions"):
            break
        else:
            des = des + " " + line
    description = des.strip("Description: ")
    versions = []
    restInfo = info[10:]
    substring = "Version :"
    for line in restInfo:
        if substring in line:
            v = line.split(": ")[1]
            versions.append(v)

    if not download:
        googlePlayLink, stars, downloads = getGooglePlayInfo(package,sourceCode)
        return package,name,summary,added,lastUpdated,currentVersion,license,category,website,sourceCode,issueTracker,changeLog,bitcoin,donate,description,versions,googlePlayLink,downloads,stars
    else:
        return package,name,versions


def makeCSV():
    print("Making the CSV file")
    apps = appNamesList
    count = 1
    with open('F-Droid App Info.csv', mode='w') as csv_file:
        fieldnames = ['Sr.','Package','Name','Summary','Added','LastUpdated','CurrentVersion','License','Category','Website','SourceCode','IssueTracker','Changelog','Bitcoin','Donate','Description','Versions','GooglePlayLink', 'Downloads', 'Stars']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for app in apps:
            info = os.popen(root+" show "+app).read().split("\n")
            print(count," - ",app)
            #print(os.popen(root+" show "+app).read())
            package,name,summary,added,lastUpdated,currentVersion,license,category,website,sourceCode,issueTracker,changeLog,bitcoin,donate,description,versions,googlePlayLink,downloads,stars = getAppInfo(info,False)
            writer.writerow({'Sr.':count,'Package':package,'Name':name,'Summary':summary,'Added':added,'LastUpdated':lastUpdated,'CurrentVersion':currentVersion,'License':license,'Category':category,'Website':website,'SourceCode':sourceCode,'IssueTracker':issueTracker,'Changelog':changeLog,'Bitcoin':bitcoin,'Donate':donate,'Description':description,'Versions':versions,'GooglePlayLink':googlePlayLink,'Downloads': downloads,'Stars': stars})
            count += 1


def getAppList():
    out = os.popen(root+" search").read()
    out = out.split("\n")
    for i in range (0,len(out)):
        if i % 2 == 0:
            list = out[i].split(" ")
            if "." in list[0]:
                appNamesList.append(list[0])


def init():
    #Following two commands should be used only once:
    os.system("go get mvdan.cc/fdroidcl")
    os.system("fdroidcl update")


if __name__ == "__main__":
    #init()
    getAppList()
    makeCSV()
    downloadApk()
