import struct

from modbus.utils import memoize
from modbus.exceptions import (IllegalDataValueError, IllegalDataAddressError)

try:
    from functools import reduce
except ImportError:
    pass

# Function related to data access.
READ_COILS = 1
READ_DISCRETE_INPUTS = 2
READ_HOLDING_REGISTERS = 3
READ_INPUT_REGISTERS = 4

WRITE_SINGLE_COIL = 5
WRITE_SINGLE_REGISTER = 6
WRITE_MULTIPLE_COILS = 15
WRITE_SINGLE_REGISTERS = 16

READ_FILE_RECORD = 20
WRITE_FILE_RECORD = 21

MASK_WRITE_REGISTER = 22
READ_WRITE_MULTIPLE_REGISTERS = 23
READ_FIFO_QUEUE = 24

# Diagnostic functions, only available when using serial line.
READ_EXCEPTION_STATUS = 7
DIAGNOSTICS = 8
GET_COMM_EVENT_COUNTER = 11
GET_COM_EVENT_LOG = 12
REPORT_SERVER_ID = 17


@memoize
def function_factory(pdu):
    """ Return function instance, based on request PDU.

    :param pdu: Array of bytes.
    :return: Instance of a function.
    """
    function_code, = struct.unpack('>B', pdu[:1])
    function_class = function_code_to_function_map[function_code]

    return function_class.create_from_request_pdu(pdu)


class Function:
    """ Abstract base class for Modbus functions. """
    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A response PDU.
        """
        raise NotImplementedError

    def execute(self, slave_id, route_map):
        """ Execute the Modbus function registered for a route.

        :param slave_id: Slave id.
        :param eindpoint: Instance of modbus.route.Map.
        :return: Result of call to endpoint.
        """
        raise NotImplementedError

    def get_response_pdu(self, data):
        """ Return response PDU.

        :param data: Reponse data of endpoint.
        :return pdu: Array of bytes.
        """
        raise NotImplementedError


class SingleBitFunction(Function):
    """ Base class with common logic for so called 'single bit' functions.
    These functions operate on single bit values, like coils and discrete
    inputs.

    """
    def __init__(self, starting_address, quantity):
        # "This function code is used to read from 1 to 2000 contiguous status
        # of coils in a remote device."
        #
        #       - MODBUS Application Protocol Specification V1.1b3, chapter 6.1
        if quantity < 1 or quantity > 2000:
            raise IllegalDataValueError('Quantify field of request must be a '
                                        'value between 0 and 2000.')

        self.starting_address = starting_address
        self.quantity = quantity

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A series of 5 bytes.
        """
        _, starting_address, quantity = struct.unpack('>BHH', pdu)

        return cls(starting_address, quantity)

    def execute(self, slave_id, route_map):
        try:
            values = []

            for address in range(self.starting_address,
                                 self.starting_address + self.quantity):
                endpoint = route_map.match(slave_id, self.function_code,
                                           address)
                values.append(endpoint(slave_id=slave_id, address=address))

            return values
        # route_map.match() returns None if no match is found. Calling None
        # results in TypeError.
        except TypeError:
            raise IllegalDataAddressError()

    def create_response_pdu(self, data):
        """ Create response from request.

        :param data: A list with 0's and/or 1's.
        :return: Byte string of at least 3 bytes.
        """
        # Reverse data list so it's easy to split it chunks (bytes) of 8 bits.
        data = list(reversed(data))
        bytes_ = [data[i:i + 8] for i in range(0, len(data), 8)]

        # Reduce each all bits per byte to a number. Byte
        # [0, 0, 0, 0, 0, 1, 1, 1] is intepreted as binary en is decimal 3.
        for index, byte in enumerate(bytes_):
            bytes_[index] = \
                reduce(lambda a, b: (a << 1) + b, list(reversed(byte)))

        # The first 2 B's of the format encode the function code (1 byte)
        # and the length (1 byte) of the following byte series. Followed by
        # a B for every byte in the series of bytes. 3 lead to the format '>BBB'
        # and 257 lead to the format '>BBBB'.
        fmt = '>BB' + 'B' * len(bytes_)
        return struct.pack(fmt, self.function_code, len(bytes_), *bytes_)


class ReadCoils(SingleBitFunction):
    """ Implement Modbus function code 01.

    The request PDU with function code 1 must be 5 bytes:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Starting address | 2              |
        | Quantity         | 2              |
        +------------------+----------------+

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x01\x00d\x00\x03')
        (1, 100, 3)

    The reponse PDU varies in length, depending on the request. Each 8 coils
    require 1 byte. The amount of bytes needed represent status of the coils to
    can be calculated with: bytes = round(quantity / 8) + 1. This response
    contains (3 / 8 + 1) = 1 byte to describe the status of the coils. The
    structure of a compleet response PDU looks like this:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Byte count       | 1              |
        | Coil status      | n              |
        +------------------+----------------+

    Assume the status of 102 is 0, 101 is 1 and 100 is also 1. This is binary
    011 which is decimal 3.

    The PDU can packed like this::

        >>> struct.pack('>BBB', function_code, byte_count, 3)
        b'\x01\x01\x03'

    """
    function_code = READ_COILS

    def __init__(self, starting_address, quantity):
        SingleBitFunction.__init__(self, starting_address, quantity)


class ReadDiscreteInputs(SingleBitFunction):
    """ Implement Modbus function code 02.

    The request PDU with function code 1 must be 5 bytes:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Starting address | 2              |
        | Quantity         | 2              |
        +------------------+----------------+

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x01\x00d\x00\x03')
        (1, 100, 3)

    The reponse PDU varies in length, depending on the request. 8 inputs
    require 1 byte. The amount of bytes needed represent status of the inputs to
    can be calculated with: bytes = round(quantity / 8) + 1. This response
    contains (3 / 8 + 1) = 1 byte to describe the status of the inputs. The
    structure of a compleet response PDU looks like this:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Byte count       | 1              |
        | Input status     | n              |
        +------------------+----------------+

    Assume the status of 102 is 0, 101 is 1 and 100 is also 1. This is binary
    011 which is decimal 3.

    The PDU can packed like this::

        >>> struct.pack('>BBB', function_code, byte_count, 3)
        b'\x01\x01\x03'

    """
    function_code = READ_DISCRETE_INPUTS

    def __init__(self, starting_address, quantity):
        SingleBitFunction.__init__(self, starting_address, quantity)

function_code_to_function_map = {
    READ_COILS: ReadCoils,
    READ_DISCRETE_INPUTS: ReadDiscreteInputs,
}
