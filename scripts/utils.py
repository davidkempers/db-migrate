import os
import git
import config
from changeset import ChangeSet
import sys
from config import logger

def get_repo(basedir):
    repopath = find_repo(basedir)
    if not repopath:
       Exception("Cannot find '.git' repository")

    return git.Repo(repopath)

def find_repo(basedir):
    if os.path.exists(os.path.join(basedir, '.git')):
        return os.path.join(basedir, '.git')
    try:
        return find_repo(os.path.abspath(os.path.join(basedir, os.pardir)))
    except Exception:
        return None


def parse_dburi(dburi):
    parts = dburi.split('@')
    username = parts[0].split('/')[0]
    password = parts[0].split('/')[-1]
    uri = parts[-1]
    return (username, password, uri)

def get_changesets(dir):

    repo = get_repo(dir)
    last_release = get_last_release(dir)
    files = []
    if last_release:
        output = repo.git.diff('--name-only', last_release)
    else:
        output = repo.git.ls_tree('-r', 'HEAD', '--name-only')
    if output:
        files = output.split('\n')
    # get pre-commit files
    output = repo.git.diff('--cached', '--name-only')
    for f in output.split('\n'):
        if f not in files:
            files.append(f)

    changesets = []
    #sqldir = dir[len(config.MOUNT_PATH):]
    if dir.endswith('/'):
        dir = dir[:-1]
    for file in files:
        file_path = os.path.join(config.MOUNT_PATH, file)
        if file_path.startswith(dir) and file.endswith('.sql') and not file.endswith('.rollback.sql'):
            logger.info('SQL file changed %s', file)
            if not os.path.exists(file_path):
                logger.debug('File has been deleted %s', file_path)
                continue
            author = get_author(dir, file)
            rollback_file = get_rollback_file(file, files)
            try:
                sql = open(file_path, 'r').read()
                f = file_path[len(dir)+1:]
                cs = ChangeSet(file=f, sql=sql, rollback_file=rollback_file, author=author)
                pos = get_dependency_position(cs, changesets)
                changesets.insert(pos, cs)
            except Exception as err:
                logger.debug(err)
    return changesets

def get_rollback_file(sqlfile, files):
    rollback_file = '%s.rollback.sql' % sqlfile[:-4]
    for f in files:
        if rollback_file == f:
            logger.debug('Rollback file for %s: %s', rollback_file, f)
            return f
    return None

def get_dependency_position(changeset, changesets):

    pos = 0
    this_name = changeset.fullname.lower()
    this_sql = changeset.sql.lower()
    for i, cs in enumerate(changesets):
        # if in the list it is referernced in the sql
        cs_name = cs.fullname.lower()
        sql = cs.sql.lower()
        if cs_name in this_sql or cs.type in ['tablespace']:
            pos = i + 1
            logger.debug('%s is in %s' % (cs_name, this_name))
        # if this object is in the sql in the list
        if this_name in sql:
            logger.debug('this %s is in %s' % (this_name, cs.name))
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
        # look in the directory to see what version might be
        versions = get_directory_versions(dir)
        if len(versions) == 0:
            return 'v1.0.0'
        return versions[-1]
    splits = last_release.split('.')
    major = splits[0]
    minor = int(splits[1]) + 1
    patch = '0'
    next_release = '%s.%s.%s' % (major, minor, patch)
    return next_release

def get_directory_versions(dir):
    logger.debug('list file in %s', dir)
    versions = []
    for version in sorted(os.listdir(dir)):
        if version[0].lower() == 'v' and not os.path.isfile(os.path.join(dir, version)):
            logger.debug('version found %s', version)
            versions.append(version)
    return versions

def get_releases(dir):
    repo = get_repo(dir)
    tags = []
    try:
        output = repo.git.ls_remote('--tags')
    except:
        logger.critical('Cannot get tags from remote server')
        # TODO clean up a bit nicer
        sys.exit(1)
    output += '\n' + repo.git.tag()
    if output:
        tags = output.split('\n')
    releases = []
    for tag in tags:
        if tag.lower().startswith('v') and tag not in releases:
            releases.append(tag)
    return sorted(releases)

def is_new_file(dir, file):
    repo = get_repo(dir)
    last_release = get_last_release(dir)
    if last_release:
        try:
            ret = repo.git.cat_file('-e', '%s:%s' % (last_release, file))
            return False
        except Exception as err:
            logger.debug('file not in release %s', err)
            # TODO check the error type
            pass
    return True

def get_author(dir, file):
    repo = get_repo(dir)
    log = repo.git.log(file)
    if not log:
        # maybe get the last commit author??
        log = repo.git.log()
    for line in log.split('\n'):
        if line.startswith('Author: '):
            # TODO convert to regex
            return line[8:].split('<')[0].strip()

    logger.info('No author found for file %s' % file)
    return os.environ['HOST_USER']
