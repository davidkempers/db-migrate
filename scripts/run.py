#!/usr/bin/python
import os
import subprocess
import sys
import select
import csv
import argparse
import migrate
import exporter
import dbdocs
from generate import create_changelog
import config
import logging

def usage(name=None):
    return '''dbmigrate <command> [options]
        Usage: dbmigrate <command> [options]
        command (required):
            generate        Create changelogs by reading SQL directory and git changes
            update          Run update database migrations
            rollback        Run database rollback
            diff            Create a db diff between update and rollback
            export          Export the schema of an existing database
            dbdoc           Output docs for the database
        common options:
            -d --database   Database uri username/password@host:port/sid (required)
            -w --working    Project directory with Git repo. Full path required.
                            Defaults to CWD (required)
            -s --sqldir     SQL directory if different to project directory. Relative
                            path to Project directory (optional)
            -l --loglevel   Change the log level. Default 'info' (optional)
        command options:
            Run dbmigrate <command> --help for command usage'''

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main(argv):

    def update(args):
        migrate.update(args.database, args.sqldir, args.version, args.outputsql, args.loglevel)

    def rollback(args):
        migrate.rollback(args.database, args.sqldir, args.version, args.outputsql, args.loglevel)

    def export(args):
        sqldir = os.path.join(config.MOUNT_PATH, args.sqldir)
        if args.parsefile:
            csvfile = os.path.join(config.MOUNT_PATH, args.parsefile)
            exporter.csv_to_sqlfile(sqldir, csvfile)
        else:
            exporter.export(args.database, sqldir)

    def diff(args):
        utils.diff(args.database, args.sqldir, args.version)

    def generate(args):
        dir = os.path.join(config.MOUNT_PATH, args.sqldir)
        create_changelog(dir, args.sqldir)

    def dbdoc(args):
        dbdocs.create(args.database, args.sqldir, args.loglevel)

    parser = MyParser(description='Migration scripts for oracle database',
                                     usage=usage())

    parser.add_argument('-d', '--database',
                     help='Database uri username/password@host:port/sid')
    parser.add_argument('-s', '--sqldir',
                     help='SQL directory relative to the working directory')
    parser.add_argument('-l', '--loglevel',
                     help='Log level (default info): debug, info, warning, error, critical')

    subparsers = parser.add_subparsers()
    parser_update = subparsers.add_parser('update')
    parser_update.add_argument('version', nargs='?', default=None, help='Version')
    parser_update.add_argument('-o', '--outputsql', action='store_true',
                               help="Output sql and not apply cnanges")
    parser_update.set_defaults(func=update)

    parser_rollback = subparsers.add_parser('rollback')
    parser_rollback.add_argument('version', nargs='?', default=None, help='Version')
    parser_rollback.add_argument('-o', '--outputsql', action='store_true',
                                 help='Output sql and not rollback')
    parser_rollback.set_defaults(func=rollback)

    parser_export = subparsers.add_parser('export')
    parser_export.set_defaults(func=export)
    parser_export.add_argument('-f', '--parsefile',
                               help='Specify a csv file to parse')

    parser_generate = subparsers.add_parser('generate')
    parser_generate.set_defaults(func=generate)
    parser_generate.add_argument('-a', '--author',
                                 help='Specify the author in the changesets')

    parser_doc = subparsers.add_parser('dbdoc')
    parser_doc.set_defaults(func=dbdoc)

    args = parser.parse_args()
    if args.loglevel and args.loglevel.upper() in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        config.logger.setLevel(logging.getLevelName(args.loglevel.upper()))

    args.func(args)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
        sys.exit(0)
    except Exception as err:
        import traceback
        sys.stderr.write(str(err) + '\n')
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write('\n')
        sys.exit(1)
