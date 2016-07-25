try:
    from socketserver import BaseRequestHandler
except ImportError:
    from SocketServer import BaseRequestHandler
from binascii import hexlify
from types import MethodType

from umodbus import log
from umodbus.route import Map


def get_server(server_class, server_address, request_handler_class):
    """ Return instance of :param:`server_class` with :param:`request_handler`
    bound to it.

    This method also binds a :func:`route` method to the server instance.

        >>> server = get_server(TcpServer, ('localhost', 502), RequestHandler)
        >>> server.serve_forever()

    :param server_class: (sub)Class of :class:`socketserver.BaseServer`.
    :param request_handler_class: (sub)Class of
        :class:`umodbus.server.RequestHandler`.
    :return: Instance of :param:`server_class`.
    """

    def route(self, slave_ids=None, function_codes=None, addresses=None):
        """ A decorator that is used to register an endpoint for a given
        rule::

            @server.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(100, 200)))  # NOQA
            def read_single_bit_values(slave_id, address):
                return random.choise([0, 1])

        :param slave_ids: A list or set with slave id's.
        :param function_codes: A list or set with function codes.
        :param addresses: A list or set with addresses.
        """
        def inner(f):
            self.route_map.add_rule(f, slave_ids, function_codes, addresses)
            return f

        return inner

    s = server_class(server_address, request_handler_class)

    s.route_map = Map()
    s.route = MethodType(route, s)

    return s


class AbstractRequestHandler(BaseRequestHandler):
    """ A subclass of :class:`socketserver.BaseRequestHandler` dispatching
    incoming Modbus requests using the server's :attr:`route_map`.

    """
    def handle(self):
        try:
            while True:
                request_adu = self.request.recv(1024)

                # When client terminates connection length of request_adu is 0.
                if len(request_adu) == 0:
                    return

                response_adu = self.process(request_adu)
                self.respond(response_adu)
        except:
            import traceback
            log.exception('Error while handling request: {0}.'
                          .format(traceback.print_exc()))
            raise

    def process(self, request_adu):
        """ Process request ADU and return response.

        :param request_adu: A bytearray containing the ADU request.
        :return: A bytearray containing the response of the ADU request.
        """
        raise NotImplementedError

    def respond(self, response_adu):
        """ Send response ADU back to client.

        :param response_adu: A bytearray containing the response of an ADU.
        """
        log.info('--> {0} - {1}.'.format(self.client_address[0],
                 hexlify(response_adu)))
        self.request.sendall(response_adu)
