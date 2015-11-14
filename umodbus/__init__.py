from logging import getLogger, NullHandler

log = getLogger('uModbus')
log.addHandler(NullHandler())

from .server import get_server  # NOQA
