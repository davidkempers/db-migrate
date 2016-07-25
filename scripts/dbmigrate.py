#!/usr/bin/python

import os.path
import utils
from subprocess import Popen, PIPE

def update(dburi, sqldir, version, outputsql=False):

    cmd = 'update'
    if outputsql:
        cmd = 'updateSQL'

    if version == 'install':
        xmlpath = os.path.join(sqldir, 'install.xml')
    else:
        xmlpath = os.path.join(sqldir, 'update.xml')
        if version is not None:
            repo = utils.get_repo(sqldir)
            # make sure we're on the correct version
            repo.git.checkout(version)

    execute(cmd, dburi, xmlpath)

def rollback(dburi, sqldir, version, outputsql=False):

    cmd = 'rollback %s' % (version)
    if outputsql:
        cmd = 'rollbackSQL %s' % (version)

    xmlpath = os.path.join(sqldir, 'update.xml')

    repo = utils.get_repo(sqldir)

    # make sure we're on the latest version for the rollback sql
    latest = utils.get_last_release(sqldir)
    print('rollback to ', latest)
    #repo.git.checkout(latest)
    try:
        # checkout the latest folder to the version we want to rollback to
        repo.git.checkout(version, '--', 'latest')
    except:
        pass

    execute(cmd, dburi, xmlpath)

def execute(cmd, dburi, xmlpath):

    username, password, uri = utils.parse_dburi(dburi)

    # now apply the update (this will also tag the database)
    cmd = 'liquibase --changeLogFile=%s --driver=oracle.jdbc.OracleDriver \
           --classpath=/usr/local/bin/ojdbc6.jar \
           --username=%s \
           --password=%s \
           --url jdbc:oracle:thin:@%s \
           --logLevel=debug %s' % (xmlpath, username, password, uri, cmd)

    print(cmd)

    p = Popen(cmd, shell=True, stdout=PIPE)
    out = p.stdout.read()

    p.wait()

    print(out)
