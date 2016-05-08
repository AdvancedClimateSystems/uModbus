"""
.. note:: This section is based on `MODBUS over Serial Line Specification and
    Implementation Guide V1.02`_.

The ADU for Modbus RTU messages differs from Modbus TCP/IP messages. Messages
send over RTU don't have a MBAP header, instead they have an Address field.
This field contains the slave id.  A CRC is appended to the message. Below all
parts of a Modbus RTU message are listed together with their byte size:

+---------------+-----------------+
| **Component** | **Size** (bytes)|
+---------------+-----------------+
| Address field | 1               |
+---------------+-----------------+
| PDU           | N               |
+---------------+-----------------+
| CRC           | 2               |
+---------------+-----------------+

The CRC is calculated from the Address field and the PDU.
"""

import struct
from serial import SerialTimeoutException

from umodbus.client.serial.redundancy_check import get_crc, validate_crc
from umodbus._functions import (create_function_from_response_pdu, ReadCoils,
                                ReadDiscreteInputs, ReadHoldingRegisters,
                                ReadInputRegisters, WriteSingleCoil,
                                WriteSingleRegister, WriteMultipleCoils,
                                WriteMultipleRegisters)


def _create_request_adu(slave_id, req_pdu):
    """ Return request ADU for Modbus RTU.

    :param slave_id: Slave id.
    :param req_pdu: Byte array with PDU.
    :return: Byte array with ADU.
    """
    first_part_adu = struct.pack('>B', slave_id) + req_pdu

    return first_part_adu + get_crc(first_part_adu)


def read_coils(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 01: Read Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadCoils()
    function.starting_address = starting_address
    function.quantity = quantity

    return _create_request_adu(slave_id, function.request_pdu)


def read_discrete_inputs(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 02: Read Discrete Inputs.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadDiscreteInputs()
    function.starting_address = starting_address
    function.quantity = quantity

    return _create_request_adu(slave_id, function.request_pdu)


def read_holding_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 03: Read Holding Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadHoldingRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return _create_request_adu(slave_id, function.request_pdu)


def read_input_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 04: Read Input Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadInputRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return _create_request_adu(slave_id, function.request_pdu)


def write_single_coil(slave_id, address, value):
    """ Return ADU for Modbus function code 05: Write Single Coil.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleCoil()
    function.address = address
    function.value = value

    return _create_request_adu(slave_id, function.request_pdu)


def write_single_register(slave_id, address, value):
    """ Return ADU for Modbus function code 06: Write Single Register.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleRegister()
    function.address = address
    function.value = value

    return _create_request_adu(slave_id, function.request_pdu)


def write_multiple_coils(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 15: Write Multiple Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleCoils()
    function.starting_address = starting_address
    function.values = values

    return _create_request_adu(slave_id, function.request_pdu)


def write_multiple_registers(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 16: Write Multiple Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleRegisters()
    function.starting_address = starting_address
    function.values = values

    return _create_request_adu(slave_id, function.request_pdu)


def parse_response_adu(resp_adu, req_adu=None):
    """ Parse response ADU and return response data. Some functions require
    request ADU to fully understand request ADU.

    :param resp_adu: Resonse ADU.
    :param req_adu: Request ADU, default None.
    :return: Response data.
    """
    resp_pdu = resp_adu[1:-2]
    validate_crc(resp_adu[:-2], resp_adu[-2:])

    req_pdu = None

    if req_adu is not None:
        req_pdu = req_adu[1:-2]

    function = create_function_from_response_pdu(resp_pdu, req_pdu)

    return function.data


def send_message(adu, serial_port):
    """ Send Modbus message over serial port and parse response. """
    try:
        serial_port.write(adu)
        response = serial_port.read(256)
    except SerialTimeoutException:
        pass

    return parse_response_adu(response, adu)
