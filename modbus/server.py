try:
    from socketserver import TCPServer, BaseRequestHandler
except ImportError:
    from SocketServer import TCPServer, BaseRequestHandler

from modbus.route import Map
from modbus.functions import function_factory
from modbus.utils import unpack_mbap


def get_server(host, port):
    return Server((host, port), RequestHandler)


class Server(TCPServer):

    def __init__(self, server_address, RequestHandlerClass):
        #super(TCPServer, self).__init__(server_address, RequestHandlerClass)
        super(TCPServer, self).__init__(('localhost', 1028), RequestHandler)
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

        return values

    def handle(self):
        adu = self.request.recv(1024).strip()

        transaction_id, protocol_id, length, unit_id = unpack_mbap(adu[:7])
        function = function_factory(adu[7:])

        values = self.dispatch_request(unit_id, function.function_code,
                                       function.starting_address)

        self.request.sendall(adu)
