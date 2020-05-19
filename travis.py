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

def createEvent(db, event):
    # print(event)
    db.collection(u'events').document().set(event)

def getResponseFromMessage(message):
    prNumber = int(message.split(' ')[3].strip('#'))
    baseURL = 'https://api.github.com/repos/aniruddhavpatil/travis101/pulls/'
    response = requests.get(url=baseURL + str(prNumber) + '/files')
    return response

def deploy(message):
    response = getResponseFromMessage(message)
    changedFiles = getChangedFiles(response)
    changedFiles = filterChangedFiles(changedFiles)
    # changedFiles = ['events/dummy1.json', 'events/dummy2.json']
    cred = credentials.Certificate('serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    for file in changedFiles:
        f = open(file, 'r')
        event = json.loads(f.read())
        createEvent(db, event)

def travis():
    repo = Repo('./')
    assert not repo.bare
    message = repo.git.log('-1', '--pretty=%B')
    # message = "Merge pull request #2 from aniruddhavpatil/dev\n\nTrigger build"
    if re.search("^Merge pull request #*", message):
        deploy(message)

    
        # print(message, prNumber)
    # changedFiles = getChangedFiles()
    # filteredFiles = filterChangedFiles(changedFiles)
    # print(filteredFiles)



if __name__ == '__main__':
    # load_dotenv()
    # print(os.getenv("HELLO"))
    travis()
