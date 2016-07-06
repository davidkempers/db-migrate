#!/usr/bin/python
import os
import subprocess
import sys
import select
import csv
import argparse

path = ''

def export(dburi):

    sqlfile = 'export-schema.sql'
    file = open(sqlfile, 'r')
    sql = file.read()

    p = subprocess.Popen(["sqlplus", dburi], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(sql)
    for row in csv.reader(iter(p.stdout.readline, '')):
        parse_row(row)
    while True:
        reads = [p.stdout.fileno(), p.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == p.stdout.fileno():
                for row in csv.reader(iter(p.stdout.readline, '')):
                    parse_row(row)
            if fd == p.stderr.fileno():
                line = p.stderr.readline()
                sys.stderr.write(line)

        if p.poll() != None:
            break


def parse_row(row):

    if len(row) == 3:
        row.insert(0, '')
    if len(row) == 4:
        schema = row[0].lower()
        name = row[1].lower()
        type = row[2].lower()
        sql = row[3].lower();
        sql = sql.replace('"', '')
        if type in ['index', 'sequence', 'table', 'tablespace']:
            location = 'install'
        else:
            location = 'latest'


        type = type + ('es' if type[-1] == 'x' else 's')


        file = os.path.join(location, type, schema, name + '.sql')
        fileout = os.path.join(path, file)

        if not os.path.exists(os.path.dirname(fileout)):
            os.makedirs(os.path.dirname(fileout))

        with open(fileout, 'w+') as fout:
            #fout.write('\n\n--changeset davkem02:' + str(i) + '\n')
            #fout.write(sql.replace('tablespace users', 'tablespace notifydata').replace('tablespace notifyidx', 'tablespace notifydata'))
            fout.write(sql)
