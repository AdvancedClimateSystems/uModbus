import sys
import struct
from logbook import StreamHandler, debug

from modbus.utils import memoize

try:
    from functools import reduce
except ImportError:
    pass

StreamHandler(sys.stdout).push_application()

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
    debug('PDU: {0}, length: {1}'.format(pdu, len(pdu)))
    function_code, = struct.unpack('>B', pdu[:1])
    debug('PDU: {0}, function_code: {1}'.format(pdu, function_code))
    function_class = function_code_to_function_map[function_code]

    return function_class.create_from_pdu(pdu)


class Function:
    """ Abstract base class for functions. """
    def __init__(self, function_code):
        self.function_code = function_code

    @staticmethod
    def create_from_request_pdu(pdu):
        """ Create instance from request PDU. """
        raise NotImplementedError

    def execute(self, endpoint):
        """ Execute the Modbus function on endpoint . """
        raise NotImplementedError

    def get_response_pdu(self, response):
        """ Return response PDU.

        :param response: Response of execution.
        :return pdu: Array of bytes.
        """
        raise NotImplementedError


class ReadCoils(Function):
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
    def __init__(self, starting_address, quantity):
        Function.__init__(self, READ_COILS)
        self.starting_address = starting_address
        self.quantity = quantity

    @staticmethod
    def create_from_pdu(pdu):
        _, starting_address, quantity = struct.unpack('>BHH', pdu)

        return ReadCoils(starting_address, quantity)

    def execute(self, slave_id, route_map):
        values = []

        for address in range(self.starting_address,
                             self.starting_address + self.quantity):
            endpoint = route_map.match(slave_id, self.function_code, address)
            values.append(endpoint(slave_id, address))

        return values

    def create_response_pdu(self, data):
        """ Create response from request. """
        decimal_total = reduce(lambda a, b: (a << 1) + b, data)
        bytes_ = [b for b in range(decimal_total, 0, -256)]

        fmt = '>BB' + 'B' * len(bytes_)
        return struct.pack(fmt, self.function_code, len(bytes_), *bytes_)


function_code_to_function_map = {
    READ_COILS: ReadCoils,
}
