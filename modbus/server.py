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
        self._endpoints = {}
        self._route_map = Map()

    def route(self, slave_ids=None, function_codes=None, addresses=None):
        """ A decorator that is used to register an endpoint for a given
        rule::

        """
        def inner(f):
            self.add_route_rule(f, slave_ids=slave_ids,
                                function_codes=function_codes,
                                addresses=addresses)
            return f

        return inner

    def add_route_rule(self, endpoint, slave_ids, function_codes, addresses):
        self._endpoints[endpoint.__name__] = endpoint
        self._route_map.add_rule(endpoint.__name__, slave_ids, function_codes,
                                 addresses)


class RequestHandler(BaseRequestHandler):

    def dispatch_request(self, slave_id, function_code, addresses):
        values = []

        for address in addresses:
            endpoint_name = self.server._route_map.match(slave_id,
                                                         function_code, address)

            if endpoint_name is None:
                raise Exception('Slave or address doesn\'t exists.')

            endpoint = self.server._endpoints[endpoint_name]

            values.append(endpoint())

        number = bin(reduce(lambda a, b: (a << 1) + b, values))
        debug('Values {0} reduced to {1}.'.format(values, number))

        return number

    def handle(self):
        adu = self.request.recv(1024).strip()
        debug('{0} --> {1}'.format(self.client_address, adu))

        transaction_id, protocol_id, length, unit_id = unpack_mbap(adu[:7])
        debug('transaction id: {0}, protocol_id: {1}, length: {2}, unid_id: '
              '{3}'.format(transaction_id, protocol_id, length, unit_id))

        function = function_factory(adu[7:])

        values = self.dispatch_request(unit_id, function.function_code,
                                       range(function.starting_address,
                                             function.starting_address + function.quantity))

        mbap = pack_mbap(transaction_id, protocol_id, unit_id, values)
        debug('Response MBAP: {0}.'.format(mbap))
        print(values)
        pdu = struct.pack('>BBB', 1, 1, 0b11)
        debug('Response PDU: {0}'.format(pdu))


        self.request.sendall(mbap + pdu)
