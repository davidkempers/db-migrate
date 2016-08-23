
import os.path
import liquibase
from config import logger

def create(dburi, sqldir, loglevel):

    cmd = 'dbDoc %s/docs' % sqldir
    xmlpath = os.path.join(sqldir, 'update.xml')
    if not os.path.exists(xmlpath):
        xmlpath = os.path.join(sqldir, 'install.xml')
        if not os.path.exists(xmlpath):
            logger.error('No changeset xml detexted in %s' % sqldir)
            return

    liquibase.execute(cmd, dburi, xmlpath, loglevel)
