from git import Repo

def getChangedFiles():
    repo = Repo('./')
    assert not repo.bare
    changedFiles = [item.a_path for item in repo.index.diff(None)]
    print(changedFiles)

def travis():
    getChangedFiles()


if __name__ == '__main__':
    travis()
