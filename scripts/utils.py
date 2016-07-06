import os
import git

def get_repo(basedir):
    repopath = find_repo(basedir)
    if not repopath:
       Exception("Cannot find '.git' repository")

    print(repopath)
    return git.Repo(repopath)

def find_repo(basedir):
    if os.path.exists(os.path.join(basedir, '.git')):
        return os.path.join(basedir, '.git')
    try:
        return find_repo(os.path.abspath(os.path.join(basedir, os.pardir)))
    except Exception:
        return None
