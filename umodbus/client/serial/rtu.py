import struct

from umodbus.client.serial.redundancy_check import get_crc, validate_crc
from umodbus._functions import (create_function_from_response_pdu, ReadCoils,
                                ReadDiscreteInputs, ReadHoldingRegisters,
                                ReadInputRegisters, WriteSingleCoil,
                                WriteSingleRegister, WriteMultipleCoils,
                                WriteMultipleRegisters)


def create_request_adu(slave_id, req_pdu):
    """ Return request ADU for Modbus RTU.

    :param slave_id: Slave id.
    :param req_pdu: Byte array with PDU.
    :return: Byte array with ADU.
    """
    first_part_adu = struct.pack('>B', slave_id) + req_pdu

    return first_part_adu + get_crc(first_part_adu)


def parse_response_adu(adu, quantity):
    """ Parse Modbus RTU response ADU. """
    validate_crc(adu[:-2], adu[-2:])

    return create_function_from_response_pdu(adu[1:-2], quantity)


def read_coils(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 01: Read Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadCoils()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_discrete_inputs(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 02: Read Discrete Inputs.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadDiscreteInputs()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_holding_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 03: Read Holding Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadHoldingRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def read_input_registers(slave_id, starting_address, quantity):
    """ Return ADU for Modbus function code 04: Read Input Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = ReadInputRegisters()
    function.starting_address = starting_address
    function.quantity = quantity

    return create_request_adu(slave_id, function.request_pdu)


def write_single_coil(slave_id, address, value):
    """ Return ADU for Modbus function code 05: Write Single Coil.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleCoil()
    function.address = address
    function.value = value

    return create_request_adu(slave_id, function.request_pdu)


def write_single_register(slave_id, address, value):
    """ Return ADU for Modbus function code 06: Write Single Register.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteSingleRegister()
    function.address = address
    function.value = value

    return create_request_adu(slave_id, function.request_pdu)


def write_multiple_coils(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 15: Write Multiple Coils.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleCoils()
    function.starting_address = starting_address
    function.values = values

    return create_request_adu(slave_id, function.request_pdu)


def write_multiple_registers(slave_id, starting_address, values):
    """ Return ADU for Modbus function code 16: Write Multiple Registers.

    :param slave_id: Number of slave.
    :return: Byte array with ADU.
    """
    function = WriteMultipleRegisters()
    function.starting_address = starting_address
    function.values = values

    return create_request_adu(slave_id, function.request_pdu)
