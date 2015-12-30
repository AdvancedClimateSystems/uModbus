import struct

try:
    from functools import reduce
except ImportError:
    pass

from umodbus.functions import function_code_to_function_map
from umodbus.exceptions import error_code_to_exception_map


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


def write_single_coil(address, value):
    """ Return PDU for Modbus function code 05: Write Single Coil.

    :param address: Address of coil you want to write to.
    :param value: 0 or 1 indicating status of coil.
    :return: Byte array with PDU.
    """
    status = 0xFF00 if value else 0x0000
    return struct.pack('>BHH', 5, address, status)


def write_single_register(address, value):
    """ Return PDU for Modbus function code 06: Write Single Register.

    :param address: Address of register you want to write to.
    :param value: Value of register.
    :return: Byte array with PDU.
    """
    return struct.pack('>BHH', 6, address, value)


def write_multiple_coils(starting_address, values):
    """ Return PDU for Modbus function code 15: Write Multiple Coils.

    :param address: Address of first coil you want to write to.
    :param value: Boolean indicating status of coil.
    :return: Byte array with PDU.
    """
    # Amount of bytes required to store status of all coils. 1 byte can store
    # statusses of 8 coils.
    bytes_required = (len(values) // 8) + 1
    bytes_ = []

    for i in range(0, len(values), 8):
        # A list with values of 1 byte.
        eight_bits = values[i:i+8]
        eight_bits.reverse()

        # Magic. Reduce a list like [1, 0, 1, 1] to its decimal representation,
        # in this particular case it's 11.
        bytes_.append(reduce(lambda value, bit: (value << 1) ^ bit,
                             eight_bits, 0))

    fmt = '>BHHB' + ('B' * bytes_required)
    return struct.pack(fmt, 15, starting_address, len(values), bytes_required,
                       *bytes_)


def write_multiple_registers(starting_address, values):
    """ Return PDU for Modbus function code 16: Write Multiple Registers.

    :param address: Address of first register you want to write to.
    :param value: List of values you want to write.
    :return: Byte array with PDU.
    """
    fmt = '>BHHB' + ('H' * len(values))
    return struct.pack(fmt, 16, starting_address, len(values),
                       2 * len(values),  *values)


def parse_response(pdu):
    """ Parse response PDU and return response data or raise error.

    :param pdu: PDU of response.
    :return: Number or list with response data.
    :raises ModbusError: When response contains error code.
    """
    function_code = struct.unpack('>B', pdu[1:2])[0]

    if function_code not in function_code_to_function_map.keys():
        raise error_code_to_exception_map[function_code]
