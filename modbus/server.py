try:
    from socketserver import TCPServer, BaseRequestHandler
except ImportError:
    from SocketServer import TCPServer, BaseRequestHandler

try:
    from functools import reduce
except ImportError:
    pass

import sys
import struct
from logbook import StreamHandler, debug, info
from modbus.route import Map
from modbus.functions import function_factory
from modbus.utils import unpack_mbap, pack_mbap

StreamHandler(sys.stdout).push_application()


def get_server(host, port):
    return Server((host, port), RequestHandler)


class Server(TCPServer):

    def __init__(self, server_address, RequestHandlerClass):
        TCPServer.__init__(self, server_address, RequestHandlerClass)
        self._route_map = Map()

    def route(self, slave_ids=None, function_codes=None, addresses=None):
        """ A decorator that is used to register an endpoint for a given
        rule::

        """
        def inner(f):
            self._route_map.add_rule(f, slave_ids, function_codes,
                                     addresses)
            return f

        return inner


class RequestHandler(BaseRequestHandler):

    def handle(self):
        adu = self.request.recv(1024).strip()
        debug('{0} --> {1}'.format(self.client_address, adu))

        transaction_id, protocol_id, length, unit_id = unpack_mbap(adu[:7])
        debug('transaction id: {0}, protocol_id: {1}, length: {2}, unid_id: '
              '{3}'.format(transaction_id, protocol_id, length, unit_id))

        function = function_factory(adu[7:])
        response = function.execute(unit_id, self.server._route_map)
        response_pdu = function.create_response_pdu(response)

        mbap = pack_mbap(transaction_id, protocol_id, len(response_pdu) + 1,
                         unit_id)

        debug('Response MBAP: {0}.'.format(mbap))
        debug('Response PDU: {0}'.format(response_pdu))

        self.request.sendall(mbap + response_pdu)
