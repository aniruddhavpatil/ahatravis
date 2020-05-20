from git import Repo
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import os
import requests
import sys
import json

def getChangedFiles(response):
    changedFileList = []
    try:
        data = response.json()
        for item in data:
            changedFileList.append(item['filename'])
        return changedFileList
    except:
        return False

def filterChangedFiles(changedFiles):
    filteredFiles = []
    regex = "^events/.*\.json$"
    for file in changedFiles:
        if re.search(regex, file):
            filteredFiles.append(file)
    return filteredFiles

def checkExists(db, event):
    # event = {
    #     "Name": "KubeConn + CloudNativeCon China 2018",
    #     "Organization": "The Linux Foundation",
    #     "Location": "\u4e0a\u6d77\u8de8\u56fd\u91c7\u8d2d\u4f1a\u5c55\u4e2d\u5fc3, Shanghai, China",
    #     "Description": "KubeCon + CloudNativeCon gathers all CNCF projects under one roof. Join leading technologists from open source cloud-native communities to further the advancement of cloud-native computing.",
    #     "Keywords": [
    #         "Linux",
    #         "Linux Foundation",
    #         "Cloud",
    #         "Asia"
    #     ],
    #     "Event Start Date": "2018-11-14T00:00:00+00:00",
    #     "Event End Date": "2018-11-15T00:00:00+00:00",
    #     "Call For Proposals Start Date": "2018-05-21T00:00:00+00:00",
    #     "Call For Proposals End Date": "2018-07-06T00:00:00+00:00",
    #     "Logo": "logo_kc_cnc_cn18w.png (https://dl.airtable.com/N31ydQOuS0CmUOb7lkdF_logo_kc_cnc_cn18w.png)",
    #     "Cover Image": "shanghai-1.jpg (https://dl.airtable.com/JiZTXVyxTz252jiYwuix_shanghai-1.jpg)",
    #     "Cover Background Color": None,
    #     "Website": "https://www.lfasiallc.com/events/kubecon-cloudnativecon-china-2018/",
    #     "Registration Link": "https://www.bagevent.com/event/kubecon-cloudnativecon-china-2018-e",
    #     "Call For Proposals Link": "https://linuxfoundation.smapply.io/prog/kubecon_cloudnativecon_china_2018/",
    #     "Twitter Handle": "linuxfoundation",
    #     "Your Twitter Handle": "PrabhanshuAttri",
    #     "Created On": "2018-06-12T02:16:00+00:00",
    #     "Approved": True
    # }
    # cred = credentials.Certificate('serviceAccount.json')
    # firebase_admin.initialize_app(cred)
    # db = firestore.client()

    existingDocs = []
    query = db.collection('events').where('Name', '==', event['Name'])
    existingDocs = [snapshot.reference for snapshot in query.stream()]
    if len(existingDocs) == 0:
        return False
    else:
        return existingDocs

def createEvent(db, event):
    try:
        db.collection('events').document().set(event)
        print("Created event:", event['Name'])
    except:
        print("Could not make entry to the database.")
    
def deleteEvent(existingDocs):
    for doc in existingDocs:
        try:
            name = doc.get().to_dict()['Name']
            doc.delete()
            print("Deleted event:", name)
        except:
            print("Could not delete event.")
    


def getResponseFromMessage(message):
    prNumber = int(message.split(' ')[3].strip('#'))
    baseURL = 'https://api.github.com/repos/aniruddhavpatil/travis101/pulls/'
    response = requests.get(url=baseURL + str(prNumber) + '/files')
    return response

def deploy(message):
    print("Merge to master detected. Starting deployment.")
    response = getResponseFromMessage(message)
    changedFiles = getChangedFiles(response)
    changedFiles = filterChangedFiles(changedFiles)
    # changedFiles = ['events/dummy6.json']
    print("Changed files:", changedFiles)
    serviceAccount = os.getenv("json")
    print("Service account",serviceAccount)
    cred = credentials.Certificate('serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    for file in changedFiles:
        f = open(file, 'r')
        event = json.loads(f.read())
        existingDocs = checkExists(db, event)
        if not existingDocs:
            createEvent(db, event)
        else:
            print("Found existing event. Overwriting.")
            deleteEvent(existingDocs)
            createEvent(db, event)

def travis():
    repo = Repo('./')
    assert not repo.bare
    message = repo.git.log('-1', '--pretty=%B')
    # message = "Merge pull request #4 from aniruddhavpatil/dev\n\nTrigger build"
    if re.search("^Merge pull request #*", message):
        deploy(message)

    
        # print(message, prNumber)
    # changedFiles = getChangedFiles()
    # filteredFiles = filterChangedFiles(changedFiles)
    # print(filteredFiles)



if __name__ == '__main__':
    travis()
