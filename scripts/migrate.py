#!/usr/bin/python

import os.path
import git
from docker import Client

def main(argv):

   try:
      opts, args = getopt.getopt(argv,"hv:w",["version=","cwd"])
   except getopt.GetoptError:
      print('%s -i <inputfile> -o <outputfile>' % (__file__))
      sys.exit(2)

    version = args.version
    dir = os.getcwd()
    latest_path = path.join(dir, 'latest')
    if not path.exists(latest_path):
       print("Cannot find 'latest' directory in %s. Run %s -h for help" % (dir, __file__))
       sys.exit(2)

    repo_path = find_repo(dir)
    if not repo_path:
       print("Cannot find '.git' repository" % (dir, __file__))
       sys.exit(2)

    repo = git.Repo(repo_path)
    if cmd == 'update':
        update(dir, repo, version, sqloutput)

    if cmd == 'rollback':
        update(dir, repo, version, sqloutput)



def update(dir, repo, version, outputsql=False):

    cmd = 'update'
    if outputsql:
        cmd = 'rollbackSQL'

    xmlpath = path.join(dir, 'update.xml')

    # make sure we're on the correct version
    repo.checkout(version)


    # now apply the update (this will also tag the database)
    execute('liquibase --changeLogFile=%s \
                       --username=system \
                       --password=oracle \
                       --url jdbc:oracle:thin:@db:1521:XE \
                       --logLevel=debug %s', % (xmlpath, cmd))

def rollback(xmlpath, version, outputsql=False):

    cmd = 'rollback %' % (version)
    if outputsql:
        cmd = 'rollbackSQL %' % (version)

    xmlpath = path.join(dir, 'update.xml')

    # make sure we're on the latest version for the rollback sql
    repo.checkout('master')

    # checkout the latest folder to the version we wont to rollback to
    repo.checkout(version, '-- latest')

    # now apply the rollback
    execute('liquibase --changeLogFile=/changelogs/sql/update.xml \
                       --username=system \
                       --password=oracle \
                       --url jdbc:oracle:thin:@db:1521:XE \
                       --logLevel=debug %s', % (xmlpath, cmd))


def find_repo(dir):
    if os.path.exists(path.join(dir, '.git')):
        return path.join(dir, '.git')
    try:
        return find_repo(os.path.abspath(os.path.join(dir, os.pardir)))
    except Exception:
        return None


def execute(cmd):
    p = Popen(cmd.split(' '), stdout=PIPE)
    out = p.stdout.read()

    p.wait()

    return out

if __name__ == '__main__':
   main(sys.argv[1:])
