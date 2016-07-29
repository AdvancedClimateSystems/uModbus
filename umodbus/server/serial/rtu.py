import struct

from umodbus.server.serial import AbstractSerialServer
from umodbus.client.serial.redundancy_check import get_crc, validate_crc


class RTUServer(AbstractSerialServer):
    def process(self, request_adu):
        """ Process request ADU and return response.

        :param request_adu: A bytearray containing the ADU request.
        :return: A bytearray containing the response of the ADU request.
        """
        validate_crc(request_adu)
        return super(RTUServer, self).process(request_adu)

    def create_response_adu(self, meta_data, response_pdu):
        """ Build response ADU from meta data and response PDU and return it.

        :param meta_data: A dict with meta data.
        :param request_pdu: A bytearray containing request PDU.
        :return: A bytearray containing request ADU.
        """
        first_part_adu = struct.pack('>B', meta_data['unit_id']) + response_pdu
        return first_part_adu + get_crc(first_part_adu)
