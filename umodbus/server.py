try:
    from socketserver import BaseRequestHandler
except ImportError:
    from SocketServer import BaseRequestHandler
from types import MethodType
from binascii import hexlify

from umodbus import log
from umodbus.route import Map
from umodbus.utils import (unpack_mbap, pack_mbap, pack_exception_pdu,
                           get_function_code_from_request_pdu)
from umodbus.functions import function_factory
from umodbus.exceptions import ModbusError, ServerDeviceFailureError


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

            @server.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(100, 200)))
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


class RequestHandler(BaseRequestHandler):
    """ A subclass of :class:`socketserver.BaseRequestHandler` dispatching
    incoming Modbus TCP/IP request using the server's :attr:`route_map`.

    """
    def handle(self):
        try:
            request_adu = self.request.recv(1024)
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
        log.debug('Lenght of received ADU is {0}.'.format(len(request_adu)))
        log.info('<-- {0} - {1}.'.format(self.client_address[0],
                 hexlify(request_adu)))
        try:
            transaction_id, protocol_id, _, unit_id = \
                unpack_mbap(request_adu[:7])

            function = function_factory(request_adu[7:])
            results = function.execute(unit_id, self.server.route_map)

            try:
                # ReadFunction's use results of callbacks to build response
                # PDU...
                response_pdu = function.create_response_pdu(results)
            except TypeError:
                # ...other functions don't.
                response_pdu = function.create_response_pdu()
        except ModbusError as e:
            function_code = get_function_code_from_request_pdu(request_adu[7:])
            response_pdu = pack_exception_pdu(function_code, e.error_code)
        except Exception as e:
            log.exception('Could not handle request: {0}.'.format(e))
            function_code = get_function_code_from_request_pdu(request_adu[7:])
            response_pdu = \
                pack_exception_pdu(function_code,
                                   ServerDeviceFailureError.error_code)

        response_mbap = pack_mbap(transaction_id, protocol_id,
                                  len(response_pdu) + 1, unit_id)

        log.debug('Response MBAP {0}'.format(response_mbap))
        log.debug('Response PDU {0}'.format(response_pdu))

        response_adu = response_mbap + response_pdu

        return response_adu

    def respond(self, response_adu):
        """ Send response ADU back to client.

        :param response_adu: A bytearray containing the response of an ADU.
        """
        log.info('--> {0} - {1}.'.format(self.client_address[0],
                 hexlify(response_adu)))
        self.request.sendall(response_adu)
