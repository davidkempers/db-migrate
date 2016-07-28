#!/usr/bin/python

import os.path
import utils
from subprocess import Popen, PIPE
import select
import sys
from config import logger

def update(dburi, sqldir, version, outputsql=False, loglevel='info'):

    cmd = 'update'
    if outputsql:
        cmd = 'updateSQL'

    if version == 'install':
        xmlpath = os.path.join(sqldir, 'install.xml')
        logger.info('Installing database changesets')
    else:
        xmlpath = os.path.join(sqldir, 'update.xml')
        if version is None:
            logger.info('Migrating database to local changesets')
        else:
            logger.info('Migrating database to version %s' % version)
            repo = utils.get_repo(sqldir)
            # make sure we're on the correct version
            repo.git.checkout(version)

    execute(cmd, dburi, xmlpath, loglevel)

def rollback(dburi, sqldir, version, outputsql=False, loglevel='info'):

    xmlpath = os.path.join(sqldir, 'update.xml')
    latest = utils.get_last_release(sqldir)
    if not latest:
        logger.warning('No releases found. Rolling back to install')
        version = 'install'
    elif version is None:
        if utils.is_new_file(sqldir, xmlpath):
            version = 'install'
        else:
            version = latest

    cmd = 'rollback %s' % (version)
    if outputsql:
        cmd = 'rollbackSQL %s' % (version)



    repo = utils.get_repo(sqldir)

    try:
        # if there is no latest then no need to get that version of the file
        # TODO think about this logic more
        if version != 'install':
            # make sure we're on the latest version for the rollback sql
            repo.git.checkout(latest)
            # checkout the latest folder to the version we want to rollback to
            repo.git.checkout(version, '--', '%s/latest' % sqldir)
        else:
            # checkout the latest folder to the version we want to rollback to
            repo.git.checkout(latest, '--', '%s/latest' % sqldir)
    except Exception as err:
        logger.critical('Cannot checkout %s:%s' % (version, str(err)))
        return

    logger.info('Rolling back to %s' % version)
    execute(cmd, dburi, xmlpath, loglevel)

def execute(cmd, dburi, xmlpath, loglevel='info'):

    username, password, uri = utils.parse_dburi(dburi)

    if not loglevel:
        loglevel = 'info'
    elif loglevel.lower() in ['error', 'critical']:
        loglevel = 'severe'
    elif loglevel.lower() not in ['debug', 'info', 'warning']:
        loglevel = 'off'

    # now apply the update (this will also tag the database)
    cmd = 'liquibase --changeLogFile=%s --driver=oracle.jdbc.OracleDriver \
           --classpath=/usr/local/bin/ojdbc6.jar \
           --username=%s \
           --password=%s \
           --url jdbc:oracle:thin:@%s \
           --logLevel=%s %s' % (xmlpath, username, password, uri, loglevel.lower(), cmd)

    logger.debug(cmd)

    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)

    while True:
        reads = [p.stdout.fileno(), p.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == p.stdout.fileno():
                read = p.stdout.readline().strip()
                sys.stdout.write(read)
            if fd == p.stderr.fileno():
                read = p.stderr.readline()
                logger.info(read)

        if p.poll() != None:
            break
    p.wait()
