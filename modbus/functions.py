import struct
from collections import namedtuple

from modbus.utils import memoize

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


ReadCoils = namedtuple('ReadCoils', ['function_code', 'starting_address',
                                     'quantity'])
"""

Implement Modbus function code 01. The request PDU with function code 1
must be 5 bytes:

    +------------------+----------------+
    | Field            | Length (bytes) |
    +------------------+----------------+
    | Function code    | 1              |
    | Starting address | 2              |
    | Quantity         | 2              |
    +------------------+----------------+

The PDU can unpacked like this::

    >>> struct.unpack('>BHH', b'\x01\x00d\x00\x03')
    (1, 100, 3)

"""

function_code_to_function_map = {
    READ_COILS: ReadCoils,
}


@memoize
def function_factory(pdu):
    """ Return function instance, based on PDU.

    :param pdu: Array of bytes.
    :return: Instance of a function.
    """
    function_code, = struct.unpack('>B', pdu[:1])
    function = function_code_to_function_map[function_code]

    return function._make(struct.unpack('>BHH', pdu))
