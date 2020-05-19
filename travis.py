from git import Repo
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from dotenv import load_dotenv
import os

def getChangedFiles():
    repo = Repo('./')
    assert not repo.bare
    message = repo.git.log('-1', '--pretty=%B')
    print(message)
    # diff = repo.git.diff('HEAD..master', name_only=True)
    # return diff.split('\n')

def filterChangedFiles(changedFiles):
    filteredFiles = []
    regex = "^events/.*\.json$"
    for file in changedFiles:
        if re.search(regex, file):
            filteredFiles.append(file)
    return filteredFiles

def createEvent(file):
    cred = credentials.Certificate('serviceAccount.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    db.collection(u'events').document().set(event)

def travis():
    changedFiles = getChangedFiles()
    # filteredFiles = filterChangedFiles(changedFiles)
    # print(filteredFiles)



if __name__ == '__main__':
    # load_dotenv()
    # print(os.getenv("HELLO"))
    travis()
