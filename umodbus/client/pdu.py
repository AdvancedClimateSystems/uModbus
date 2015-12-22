"""
.. note:: This section is based on `MODBUS Application Protocol Specification
    V1.1b3`_

The Protocol Data Unit (PDU) is the request or response message and is
indepedent of the underlying communication layer. This module only implements
requests PDU's.

A request PDU contains two parts: a function code and request data. A response
PDU contains the function code from the request and response data. The general
structure is listed in table below:

+---------------+-----------------+
| **Field**     | **Size** (bytes)|
+---------------+-----------------+
| Function code | 1               |
+---------------+-----------------+
| data          | N               |
+---------------+-----------------+

Below you see the request PDU with function code 1, requesting status of 3
coils, starting from coil 100::

    >>> req_pdu = b'\x01\x00d\x00\x03'
    >>> function_code = req_pdu[:1]
    >>> function_code
    b'\x01'
    >>> starting_address = req_pdu[1:3]
    >>> starting_address
    b'\x00d'
    >>> quantity = req_pdu[3:]
    >>> quantity
    b'\x00\x03'

A response PDU could look like this::

    >>> resp_pdu = b'\x01\x01\x06'
    >>> function_code = resp_pdu[:1]
    >>> function_code
    b'\x01'
    >>> byte_count = resp[1:2]
    >>> byte_count
    b'\x01'
    >>> coil_status = resp[2:]
    'b\x06'

.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
"""
import struct


def read_coils(starting_address, quantity):
    """ Return PDU for Modbus function code 01: Read Coils.

    :param starting_address: Number with address of first coil.
    :param quantity: Number with amount of coils to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 1, starting_address, quantity)


def read_discrete_inputs(starting_address, quantity):
    """ Return PDU for Modbus function code 02: Read Discret Inputs.

    :param starting_address: Number with address of first discrete input.
    :param quantity: Number with amount of discrete inputs to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 2, starting_address, quantity)


def read_holding_registers(starting_address, quantity):
    """ Return PDU for Modbus function code 03: Read Input Registers.

    :param starting_address: Number with address of first holding register.
    :param quantity: Number with amount of holding registers to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 3, starting_address, quantity)


def read_input_registers(starting_address, quantity):
    """ Return PDU for Modbus function code 04: Read Input Registers.

    :param starting_address: Number with address of first input register.
    :param quantity: Number with amount of input registers to read.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 4, starting_address, quantity)
