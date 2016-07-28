
import logging
import sys


MOUNT_PATH = '/changelogs'


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logging.StreamHandler(sys.stderr)
