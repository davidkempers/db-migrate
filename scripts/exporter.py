#!/usr/bin/python
import os
import subprocess
import sys
import select
import csv
import argparse
import re
from changeset import ChangeSet
import utils
from config import logger

def export(dburi, sqldir, users=''):

    exportdir = '/scripts/export'
    csvfile = '/tmp/schema.csv'
    sqlconf = open(os.path.join(exportdir, 'sqlplus.conf'), 'r').read()
    # sanitise the user string
    user_list = re.escape(users).upper().split(',')
    # enclose in single quotes
    users = ', '.join("'" + user + "'" for user in user_list)
    changesets = []
    for f in os.listdir(exportdir):
        if f.endswith('.sql'):
            sql = open(os.path.join(exportdir, f), 'r').read()
            sql = sql.format(users=users)
            sql = sqlconf.format(csvfile=csvfile, sql=sql)

            cmd = 'sqlplus -s %s <<EOF\n%s\nEOF' % (dburi, sql)
            logger.debug(cmd)
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            #sys.stderr.write('run sql' + dburi)
            for row in p.stdout.readline():
                logger.debug(row.strip())
            exitcode = p.wait()
            # if non zero print the error
            if (exitcode):
                logger.error('Error when running SQL:\n%s', open(csvfile, 'r').read())
            else:
                logger.debug('Finished exporting %s', f)

            if os.path.isfile(csvfile):
                csv_to_sqlfile(sqldir, csvfile)
                os.remove(csvfile)


def csv_to_sqlfile(outdir, csvfile):
    with open(csvfile, 'r') as f:
        for row in csv.reader(f):
            if len(row) == 4:
                schema = row[1].lower().strip()
                name = row[2].lower().strip()
                type = row[3].lower().strip()
                sql = row[0]
                sql = sql.replace('"', '')
                sql = correct_sql(type, name, sql)
                if type in ['package', 'package_spec', 'package_body', 'trigger', 'view', 'function', 'type_spec', 'procedure', 'synonym']:
                    location = 'latest'
                else:
                    location = 'install'

                cs = ChangeSet(location=location, schema=schema, name=name, type=type, sql=sql)

                fileout = os.path.join(outdir, cs.file)

                if not os.path.exists(os.path.dirname(fileout)):
                    os.makedirs(os.path.dirname(fileout))

                with open(fileout, 'w+') as fout:
                    fout.write(cs.sql)

def correct_sql(type, name, sql):
    # just hack this for now
    if type == 'tablespace':
        if 'datafile' in sql:
            return """create tablespace %s datafile
  '%s_01.dbf' size 30M autoextend on
  logging online permanent blocksize 8192
  extent management local autoallocate default
 nocompress  segment space management auto""" % (name, name)
        else:
            return """create temporary tablespace %s tempfile
  '%s_01.dbf' size 32m
  autoextend on
  next 32m maxsize 2048m
  extent management local"""  % (name, name)

    if type in ['object_grant', 'role_grant', 'system_grant']:
        return sql.replace('\n', ';\n')
    if type == 'table':
        sql = sql.replace('segment creation deferred', 'segment creation immediate')
        ret = []
        constraint = False
        for line in sql.split('\n'):
            line = line.rstrip(' ')
            if 'constraint' in line and 'foreign key' in line:
                constraint = True
            elif constraint and 'references' in line:
                constraint = False
                if not line.endswith(','):
                    if len(ret) == 0:
                        print(line, sql, ret)
                    elif ret[-1].endswith(','):
                        ret[-1] = ret[-1].rstrip(',')
            else:
                ret.append(line)
        return '\n'.join(ret)
    if type == 'trigger':
        ret = []
        for line in sql.split('\n'):
            if 'alter trigger ' not in line:
                ret.append(line)
        return '\n'.join(ret)
    return sql
