#!/usr/bin/python
import os
import subprocess
import sys
import select
import csv
import argparse
import re
from changeset import ChangeSet
from generate import create_installxml

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
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
            #p.stdin.write(sql)
            sys.stderr.write(cmd)
            sys.stderr.write('\n')
            #sys.stderr.write('run sql' + dburi)
            for row in p.stdout.readline():
                sys.stderr.write(row)
            exitcode = p.wait()
            # if non zero print the error
            if (exitcode):
                sys.stderr.write(open(csvfile, 'r').read())

            sys.stderr.write('all read\n')

            if os.path.isfile(csvfile):
                changesets = csv_to_sqlfile(sqldir, csvfile, changesets)
                os.remove(csvfile)

    #generate(sqldir, changesets)
    create_installxml(sqldir, changesets)

def csv_to_sqlfile(outdir, csvfile, changesets=[]):
    with open(csvfile, 'r') as f:
        for row in csv.reader(f):
            if len(row) == 4:
                schema = row[1].lower().strip()
                name = row[2].lower().strip()
                type = row[3].lower().strip()
                sql = row[0].lower().strip();
                sql = sql.replace('"', '')
                if type in ['index', 'sequence', 'table', 'tablespace']:
                    location = 'install'
                else:
                    location = 'latest'


                type = type + ('es' if type[-1] == 'x' else 's')

                cs = ChangeSet(location=location, schema=schema, name=name, type=type, sql=sql)
                pos = get_dependency_pos(cs, changesets)
                changesets.insert(pos, cs)

                fileout = os.path.join(outdir, cs.file)

                if not os.path.exists(os.path.dirname(fileout)):
                    os.makedirs(os.path.dirname(fileout))

                xml += u'<include file="%s" relativeToChangelogFile="true"/>\n' % (cs.file.replace('\\', '/'))

                with open(fileout, 'w+') as fout:
                    #fout.write('\n\n--changeset davkem02:' + str(i) + '\n')
                    #fout.write(sql.replace('tablespace users', 'tablespace notifydata').replace('tablespace notifyidx', 'tablespace notifydata'))
                    fout.write(cs.sql)

    return changesets

def generate(outdir, changesets):

    xml = u"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<databaseChangeLog xmlns="http://www.liquibase.org/xml/ns/dbchangelog/1.9"
                   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                   xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog/1.9 http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-1.9.xsd">\n"""

    for cs in changesets:
        fileout = os.path.join(outdir, cs.file)

        if not os.path.exists(os.path.dirname(fileout)):
            os.makedirs(os.path.dirname(fileout))

        xml += u'<include file="%s" relativeToChangelogFile="true"/>\n' % (cs.file.replace('\\', '/'))

        with open(fileout, 'w+') as fout:
            #fout.write('\n\n--changeset davkem02:' + str(i) + '\n')
            #fout.write(sql.replace('tablespace users', 'tablespace notifydata').replace('tablespace notifyidx', 'tablespace notifydata'))
            fout.write(cs.sql)

    xml += u"""<changeSet author="MajorVersion" id="1" />
</databaseChangeLog>"""


    #with open(outdir + '/install.xml', 'w+') as fout:
    #    fout.write(xml)
