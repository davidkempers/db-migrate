import os
import git
import config
from changeset import ChangeSet

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
        output = repo.git.diff('--name-only', last_release)
        if output:
            files += output.split('\n')
    # get pre-commit files
    output = repo.git.diff('--cached', '--name-only')
    if output:
        files += output.split('\n')

    changesets = []
    #sqldir = dir[len(config.MOUNT_PATH):]
    if dir.endswith('/'):
        dir = dir[:-1]
    for f in files:
        file_path = os.path.join(config.MOUNT_PATH, f)
        if file_path.startswith(dir) and f.endswith('.sql'):
            f = file_path[len(dir)+1:]
            #if not os.path.exists(file_path):
            #    continue
            splits = f.split('/')
            if len(splits) == 4:
                location = splits[0]
                schema = splits[2]
                name = splits[3][:-4]
                type = splits[1]
                sql = '';#open(file_path, 'r').read()
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
    tags = []
    output = repo.git.ls_remote('--tags')
    print('output', output)
    output += '\n' + repo.git.tag()
    if output:
        tags = output.split('\n')
    print('output', output)
    releases = []
    for tag in tags:
        if tag.lower().startswith('v') and tag not in releases:
            releases.append(tag)
    print('releases', tags)
    return sorted(releases)

def is_new_file(dir, file):
    repo = get_repo(dir)
    last_release = get_last_release(dir)
    if last_release:
        try:
            repo.git('cat-file -e %s:%s' % (last_release, file))
            return False
        except:
            pass
    return True
