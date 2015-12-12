import os
from logging import getLogger, NullHandler

log = getLogger('uModbus')
log.addHandler(NullHandler())

from .config import Config  # NOQA
conf = Config()

from .server import get_server, RequestHandler  # NOQA
