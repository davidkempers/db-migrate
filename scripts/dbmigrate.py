#!/usr/bin/python

import os.path
import utils

def update(sqldir, dburi, version, outputsql=False):

    cmd = 'update'
    if outputsql:
        cmd = 'updateSQL'

    xmlpath = os.path.join(sqldir, 'update.xml')
    if version == 'install':
        xmlpath = os.path.join(sqldir, 'install.xml')

    repo = utils.get_repo(sqldir)
    # make sure we're on the correct version
    repo.git.checkout(version)

    execute(cmd, dburi, xmlpath)

def rollback(dir, version, outputsql=False):

    cmd = 'rollback %' % (version)
    if outputsql:
        cmd = 'rollbackSQL %' % (version)

    xmlpath = os.path.join(dir, 'update.xml')

    # make sure we're on the latest version for the rollback sql
    repo.git.checkout('master')

    # checkout the latest folder to the version we wont to rollback to
    repo.git.checkout(version, '-- latest')

    execute(cmd, dburi, xmlpath)

def execute(cmd, dburi, xmlpath):
    parts = dburi.split('@')
    uri = parts[-1]
    username = parts[0].split('/')[0]
    password = parts[0].split('/')[1]

    # now apply the update (this will also tag the database)
    execute('liquibase --changeLogFile=%s \
                       --username=%s \
                       --password=%s \
                       --url jdbc:oracle:thin:@%s \
                       --logLevel=debug %s' %
                        (xmlpath, username, password, uri, cmd))


    p = Popen(cmd.split(' '), stdout=PIPE)
    out = p.stdout.read()

    p.wait()

    print(out)
