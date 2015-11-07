from logging import getLogger

try:
    from logging import NullHandler
# For Python 2.7 compatibility.
except ImportError:
    from logging import Handler

    class NullHandler(Handler):
        def emit(self, record):
            pass

log = getLogger('tolk')
log.addHandler(NullHandler())
