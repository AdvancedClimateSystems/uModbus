import struct

from modbus import log
from modbus.utils import memoize
from modbus.exceptions import IllegalDataValueError, IllegalDataAddressError

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


class ReadFunction(object):
    """ Abstract base class for Modbus read functions. """
    def __init__(self, starting_address, quantity):
        if quantity < 1 or quantity > self.max_quantity:
            raise IllegalDataValueError('Quantify field of request must be a '
                                        'value between 0 and '
                                        '{0}.'.format(self.max_quantity))

        self.starting_address = starting_address
        self.quantity = quantity

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A response PDU.
        """
        _, starting_address, quantity = struct.unpack('>BHH', pdu)

        return cls(starting_address, quantity)

    def execute(self, slave_id, route_map):
        """ Execute the Modbus function registered for a route.

        :param slave_id: Slave id.
        :param eindpoint: Instance of modbus.route.Map.
        :return: Result of call to endpoint.
        """
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


class WriteSingleValueFunction(object):
    """ Abstract base class for Modbus write functions. """
    def __init__(self, address, value):
        self.address = address
        self.value = value

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A response PDU.
        """
        _, address, value = struct.unpack('>BHH', pdu)

        return cls(address, value)

    def execute(self, slave_id, route_map):
        """ Execute the Modbus function registered for a route.

        :param slave_id: Slave id.
        :param eindpoint: Instance of modbus.route.Map.
        """
        endpoint = route_map.match(slave_id, self.function_code, self.address)
        try:
            endpoint(slave_id=slave_id, address=self.address, value=self.value)
        # route_map.match() returns None if no match is found. Calling None
        # results in TypeError.
        except TypeError:
            raise IllegalDataAddressError()

    def create_response_pdu(self):
        return struct.pack('>BHH', self.function_code, self.address,
                           self.value)


class SingleBitResponse(object):
    """ Base class with common logic for so called 'single bit' functions.
    These functions operate on single bit values, like coils and discrete
    inputs.

    """
    def create_response_pdu(self, data):
        """ Create response pdu.

        :param data: A list with 0's and/or 1's.
        :return: Byte array of at least 3 bytes.
        """
        log.debug('Create single bit response pdu {0}.'.format(data))
        bytes_ = [data[i:i + 8] for i in range(0, len(data), 8)]

        # Reduce each all bits per byte to a number. Byte
        # [0, 0, 0, 0, 0, 1, 1, 1] is intepreted as binary en is decimal 3.
        for index, byte in enumerate(bytes_):
            bytes_[index] = \
                reduce(lambda a, b: (a << 1) + b, list(reversed(byte)))

        log.debug('Reduced single bit data to {0}.'.format(bytes_))
        # The first 2 B's of the format encode the function code (1 byte)
        # and the length (1 byte) of the following byte series. Followed by
        # a B for every byte in the series of bytes. 3 lead to the format
        # '>BBB' and 257 lead to the format '>BBBB'.
        fmt = '>BB' + 'B' * len(bytes_)
        return struct.pack(fmt, self.function_code, len(bytes_), *bytes_)


class MultiBitResponse(object):
    """ Base class with common logic for so called 'multi bit' functions.
    These functions operate on byte values, like input registers and holding
    registers. By default values are 16 bit and unsigned.

    """
    def create_response_pdu(self, data):
        """ Create response pdu.

        :param data: A list with values.
        :return: Byte array of at least 4 bytes.
        """
        log.debug('Create multi bit response pdu {0}.'.format(data))
        fmt = '>BB' + 'H' * len(data)

        return struct.pack(fmt, self.function_code, len(data) * 2, *data)


class ReadCoils(ReadFunction, SingleBitResponse):
    """ Implement Modbus function code 01.

    The request PDU with function code 01 must be 5 bytes:

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
    max_quantity = 2000
    # "This function code is used to read from 1 to 2000 contiguous status
    # of coils in a remote device."
    #
    #       - MODBUS Application Protocol Specification V1.1b3, chapter 6.1

    def __init__(self, starting_address, quantity):
        ReadFunction.__init__(self, starting_address, quantity)


class ReadDiscreteInputs(ReadFunction, SingleBitResponse):
    """ Implement Modbus function code 02.

    The request PDU with function code 02 must be 5 bytes:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Starting address | 2              |
        | Quantity         | 2              |
        +------------------+----------------+

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x02\x00d\x00\x03')
        (2, 100, 3)

    The reponse PDU varies in length, depending on the request. 8 inputs
    require 1 byte. The amount of bytes needed represent status of the inputs
    to can be calculated with: bytes = round(quantity / 8) + 1. This response
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
        b'\x02\x01\x03'

    """
    function_code = READ_DISCRETE_INPUTS
    max_quantity = 2000
    # "This function code is used to read from 1 to 2000 contiguous status
    # of coils in a remote device."
    #
    #       - MODBUS Application Protocol Specification V1.1b3, chapter 6.2

    def __init__(self, starting_address, quantity):
        ReadFunction.__init__(self, starting_address, quantity)


class ReadHoldingRegisters(ReadFunction, MultiBitResponse):
    """ Implement Modbus function code 03.

    The request PDU with function code 03 must be 5 bytes:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Starting address | 2              |
        | Quantity         | 2              |
        +------------------+----------------+

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x03\x00d\x00\x03')
        (3, 100, 3)

    The reponse PDU varies in length, depending on the request. By default,
    holding registers are 16 bit (2 bytes) values. So values of 3 holding
    registers is expressed in 2 * 3 = 6 bytes.

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Byte count       | 1              |
        | Register value   | quantity * 2   |
        +------------------+----------------+

    Assume the value of 100 is 8, 101 is 0 and 102 is also 15.

    The PDU can packed like this::

        >>> data = [8, 0, 15]
        >>> struct.pack('>BBHHH', function_code, len(data) * 2, *data)
        '\x03\x06\x00\x08\x00\x00\x00\x0f'

    """
    function_code = READ_HOLDING_REGISTERS
    max_quantity = 125

    def __init__(self, starting_address, quantity):
        ReadFunction.__init__(self, starting_address, quantity)


class ReadInputRegisters(ReadFunction, MultiBitResponse):
    """ Implement Modbus function code 04.

    The request PDU with function code 04 must be 5 bytes:

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Starting address | 2              |
        | Quantity         | 2              |
        +------------------+----------------+

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x04\x00d\x00\x03')
        (4, 100, 3)

    The reponse PDU varies in length, depending on the request. By default,
    holding registers are 16 bit (2 bytes) values. So values of 3 holding
    registers is expressed in 2 * 3 = 6 bytes.

        +------------------+----------------+
        | Field            | Length (bytes) |
        +------------------+----------------+
        | Function code    | 1              |
        | Byte count       | 1              |
        | Register value   | quantity * 2   |
        +------------------+----------------+

    Assume the value of 100 is 8, 101 is 0 and 102 is also 15.

    The PDU can packed like this::

        >>> data = [8, 0, 15]
        >>> struct.pack('>BBHHH', function_code, len(data) * 2, *data)
        '\x04\x06\x00\x08\x00\x00\x00\x0f'

    """
    function_code = READ_INPUT_REGISTERS
    max_quantity = 125

    def __init__(self, starting_address, quantity):
        ReadFunction.__init__(self, starting_address, quantity)


class WriteSingleCoil(WriteSingleValueFunction):
    function_code = WRITE_SINGLE_COIL

    def __init__(self, address, value):
        WriteSingleValueFunction.__init__(self, address, value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """ Validate if value is 0 or 0xFF00. """
        # "A value of FF00 hex requests the output to be ON. A value of 0000
        # requests to be OFF. All other values are illegal and will not affect
        # the output."
        #
        #    - MODBUS Application Protocol Specification V1.1b3, chapter 6.5.
        if value not in [0, 0xFF00]:
            raise IllegalDataValueError

        self._value = value


function_code_to_function_map = {
    READ_COILS: ReadCoils,
    READ_DISCRETE_INPUTS: ReadDiscreteInputs,
    READ_HOLDING_REGISTERS: ReadHoldingRegisters,
    READ_INPUT_REGISTERS: ReadInputRegisters,
    WRITE_SINGLE_COIL: WriteSingleCoil,
}
