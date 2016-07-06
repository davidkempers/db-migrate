#!/usr/bin/python
import os
import subprocess
import sys
import select
import csv
import argparse
import dbmigrate
import export

path = ''

def usage(name=None):
    return '''dbmigrate <command> [options]
	Usage: dbmigrate <command> [options]
	command (required):
	    generate        Create changelogs by reading SQL directory and git changes
	    update          Run update database migrations
	    rollback        Run database rollback
	    diff            Create a db diff between update and rollback
	    export          Export the schema of an existing database
	common options:
	    -d --database   Database uri username/password@host:port/sid (required)
	    -w --working    Project directory with Git repo. Full path required.
	                    Defaults to CWD (required)
	    -s --sqldir     SQL directory if different to project directory. Relative
	                    path to Project directory (optional)
	command options:
	    Run dbmigrate <command> --help for command usage'''

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main(argv):

    def update(args):
        dbmigrate.update(args.database, args.sqldir, args.version)

    def rollback(args):
        dbmigrate.update(args.database, args.sqldir, args.version)

    def export(args):
        export.export(args.database, args.sqldir, args.version)

    def diff(args):
        utils.diff(args.database, args.sqldir, args.version)

    parser = MyParser(description='Migration scripts for oracle database',
                                     usage=usage())
    subparsers = parser.add_subparsers()
    parser_update = subparsers.add_parser('update')
    parser_update.add_argument('-d', '--database',
                        help='Database uri username/password@host:port/sid')
    parser_update.add_argument('-s', '--sqldir',
                        help='SQL directory relative to the working directory')
    parser_update.add_argument("version", help="Version")
    parser_update.set_defaults(func=update)
    args = parser.parse_args()
    args.func(args)


    sys.exit(0)

if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except Exception as err:
        import traceback
        sys.stderr.write(str(err) + '\n')
        sys.stderr.write(traceback.format_exc())
        sys.stderr.write('\n')
        sys.exit(1)

'''#!/bin/bash

# entry point script for docker
echo $@
cmd=$1
shift

if [[ $cmd == "update" ]]; then
    python /scripts/migrate.py {$@}
elif [[ $cmd == "rollback" ]]; then
    python /scripts/migrate.py {$@}
elif [[ $cmd == "diff" ]]; then
    python /scripts/migrate.py {$@}
elif [[ $cmd == "generate" ]]; then
    python /scripts/generate.py {$@}
elif [[ $cmd == "export" ]]; then
    python /scripts/export.py {$@}
fi'''
