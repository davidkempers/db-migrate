#!/usr/bin/python

import os.path
import utils
import subprocess
import select
import sys
from config import logger
import liquibase

def update(dburi, sqldir, version, outputsql=False, loglevel='info'):

    cmd = 'update'
    if outputsql:
        cmd = 'updateSQL'

    if version == 'install':
        if utils.is_new_file(sqldir, 'install.xml'):
            logger.warning('You should commit install.xml to prevent this file being overwritten with new sql file changes')

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

    liquibase.execute(cmd, dburi, xmlpath, loglevel)
    
    
    show_invalid_object(dburi)
    
    compile_invalid_objects(dburi)
    
    show_invalid_object(dburi)
    

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
    liquibase.execute(cmd, dburi, xmlpath, loglevel)

    
def show_invalid_object(dburi):

    sql = '''select status,count(*)
             from dba_objects
             group by status
             order by status;'''
    cmd = 'sqlplus -s %s <<EOF\n%s\nEOF' % (dburi, sql)
    logger.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    
    logger.info('Invalid Objects')
    logger.info(p.stdout.read())
                
def compile_invalid_objects(dburi):

    sql = '''set head off
    select 'alter '||object_type||' '||owner||'.'||object_name|| ' compile;'
from dba_objects
where owner='YOURSCHEMA' and
status='INVALID' and
object_type <> 'PACKAGE BODY'
union
select 'alter package '||owner||'.'||object_name||' compile body;'
from dba_objects
where 
status='INVALID' and
object_type = 'PACKAGE BODY';'''
             
    cmd = 'sqlplus -s %s <<EOF\n%s\nEOF' % (dburi, sql)
    logger.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    
    
    logger.info('Compiling Objects')
    
    sql = p.stdout.read()
   
    logger.info(sql)
    
    cmd = 'sqlplus -s %s <<EOF\n%s\nEOF' % (dburi, sql)
    logger.debug(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
       
    logger.info(p.stdout.read())