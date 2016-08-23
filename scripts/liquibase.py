import os.path
import utils
from subprocess import Popen, PIPE
import select
import sys
from config import logger


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

    p = Popen(cmd, shell=True, stderr=PIPE, close_fds=True)

    while True:
        #reads = [p.stdout.fileno(), p.stderr.fileno()]
        reads = [p.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == p.stderr.fileno():
                read = p.stderr.readline()
                logger.info(read.strip())
            #if fd == p.stdout.fileno():
            #    read = p.stdout.read()
            #    sys.stdout.write(read)

        if p.poll() != None:
            break
    p.wait()
