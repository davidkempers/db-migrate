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


def parse_dburi(dburi):
    print(dburi)
    parts = dburi.split('@')
    username = parts[0].split('/')[0]
    password = parts[0].split('/')[-1]
    uri = parts[-1]
    return (username, password, uri)

def get_changesets(dir):
    repo = get_repo(dir)
    last_release = get_last_release(dir)
    files = []
    print('last release', last_release)
    if last_release:
        files = repo.git.diff('--nameonly %s' % last_release)
        if output:
            files += output.split('\n')
    #files.append(repo.git.diff_index('--cached', 'HEAD'))
    output = repo.git.diff('--cached', '--name-only')
    if output:
        files += output.split('\n')
    changesets = []
    for f in files:
        if dir in f:
            file_path = os.path.join(dir, f)
            if not os.path.exists(file_path):
                continue
            splits = f.split('/')
            location = splits[0]
            schema = splits[1]
            name = splits[2]
            type = splits[3]
            sql = open(file_path, 'r').read()
            cs = ChangeSet(location=location, schema=schema, name=name, type=type, sql=sql)
            pos = get_dependency_position(cs, changesets)
            changesets.insert(pos, cs)
    return changesets

def get_dependency_position(changeset, changesets):
    pos = 0
    this_name = changeset.fullname
    for i, cs in enumerate(changesets):
        # if in the list it is referernced in the sql
        cs_name = cs.fullname
        if cs_name in cs.sql:
            pos = i + 1
            print ('%s is in %s' % (cs_name, this_name))
        # if this object is in the sql in the list
        # but
        if this_name in cs.sql:
            print ('this %s is in %s' % (this_name, cs.name))
            pos = i
            break
    return pos

def get_last_release(dir):
    releases = get_releases(dir)
    if not releases:
        return None
    last_release = releases[-1]
    return last_release

def get_next_release(dir):
    last_release = get_last_release(dir)
    if not last_release:
        return '1.0.0'
    splits = last_release.split('.')
    major = splits[0]
    minor = splits[1]
    patch = '0'
    next_release = '%s.%s.%s' % (major, minor, patch)
    return next_release

def get_directory_versions(dir):
    versions = []
    for version in sorted(os.listdir(dir)):
        if version[0].lower() == 'v' and not os.path.isfile(os.path.join(dir, version)):
            versions.append(version)
    return versions

def get_releases(dir):
    repo = get_repo(dir)
    branches = repo.git.branch('-r')
    print(branches)
    return
    releases = []
    for branch in sorted(branches):
        if branch[0] != 'v':
            releases.append(branch)
    return releases

def is_new_file(dir, file):
    repo = get_repo(dir)
    last_release = get_last_release(dir)
    try:
        repo.git('cat-file -e %s:%s')
        return True
    except:
        return False
