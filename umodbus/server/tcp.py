from binascii import hexlify

from umodbus import log
from umodbus.server import AbstractRequestHandler
from umodbus.utils import (unpack_mbap, pack_mbap, pack_exception_pdu,
                           get_function_code_from_request_pdu)
from umodbus.functions import function_factory
from umodbus.exceptions import ModbusError, ServerDeviceFailureError


class RequestHandler(AbstractRequestHandler):
    """ A subclass of :class:`socketserver.BaseRequestHandler` dispatching
    incoming Modbus TCP/IP request using the server's :attr:`route_map`.

    """
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

        log.debug('Response MBAP {0}'.format(hexlify(response_mbap)))
        log.debug('Response PDU {0}'.format(hexlify(response_pdu)))

        response_adu = response_mbap + response_pdu

        return response_adu
