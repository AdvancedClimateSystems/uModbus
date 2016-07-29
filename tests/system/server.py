try:
    from socketserver import TCPServer
except ImportError:
    from SocketServer import TCPServer

from umodbus import conf
from umodbus.server.tcp import get_server, RequestHandler

conf.SIGNED_VALUES = True

app = get_server(TCPServer, ('localhost', 0), RequestHandler)

import route
route.bind_routes(app)
