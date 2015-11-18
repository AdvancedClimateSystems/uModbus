from __future__ import division
import struct
from math import ceil
from functools import reduce

from umodbus import log
from umodbus import conf
from umodbus.utils import memoize, get_function_code_from_request_pdu
from umodbus.exceptions import (IllegalFunctionError, IllegalDataValueError,
                                IllegalDataAddressError)


# Function related to data access.
READ_COILS = 1
READ_DISCRETE_INPUTS = 2
READ_HOLDING_REGISTERS = 3
READ_INPUT_REGISTERS = 4

WRITE_SINGLE_COIL = 5
WRITE_SINGLE_REGISTER = 6
WRITE_MULTIPLE_COILS = 15
WRITE_MULTIPLE_REGISTERS = 16

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
    function_code = get_function_code_from_request_pdu(pdu)
    try:
        function_class = function_code_to_function_map[function_code]
    except KeyError:
        raise IllegalFunctionError(function_code)

    return function_class.create_from_request_pdu(pdu)


class ReadFunction(object):
    """ Abstract base class for Modbus read functions. """
    def __init__(self, starting_address, quantity):
        if not (1 <= quantity <= self.max_quantity):
            raise IllegalDataValueError('Quantify field of request must be a '
                                        'value between 0 and '
                                        '{0}.'.format(self.max_quantity))

        self.starting_address = starting_address
        self.quantity = quantity

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A request PDU.
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
        fmt = '>BH' + self.format_character
        return struct.pack(fmt, self.function_code, self.address, self.value)


class WriteMultipleValueFunction(object):
    """ Abstract base class for Modbus write functions. """
    def __init__(self, starting_address, values):
        self.starting_address = starting_address
        self.values = values

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
        """
        for index, value in enumerate(self.values):
            address = self.starting_address + index
            endpoint = route_map.match(slave_id, self.function_code, address)

            try:
                endpoint(slave_id=slave_id, address=address, value=value)
            # route_map.match() returns None if no match is found. Calling None
            # results in TypeError.
            except TypeError:
                raise IllegalDataAddressError()

    def create_response_pdu(self):
        """ Create response pdu.

        :param data: A list with values.
        :return: Byte array 5 bytes.
        """
        return struct.pack('>BHH', self.function_code, self.starting_address,
                           len(self.values))


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
        # The first 2 B's of the format encode the function code (1 byte) and
        # the length (1 byte) of the following byte series. Followed by # a B
        # for every byte in the series of bytes. 3 lead to the format '>BBB' and
        # 257 lead to the format '>BBBB'.
        fmt = '>BB' + self.format_character * len(bytes_)
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
        fmt = '>BB' + self.format_character * len(data)

        return struct.pack(fmt, self.function_code, len(data) * 2, *data)


class ReadCoils(ReadFunction, SingleBitResponse):
    """ Implement Modbus function code 01.

        "This function code is used to read from 1 to 2000 contiguous status of
        coils in a remote device. The Request PDU specifies the starting
        address, i.e. the address of the first coil specified, and the number of
        coils. In the PDU Coils are addressed starting at zero. Therefore coils
        numbered 1-16 are addressed as 0-15.

        The coils in the response message are packed as one coil per bit of the
        data field. Status is indicated as 1= ON and 0= OFF. The LSB of the
        first data byte contains the output addressed in the query. The other
        coils follow toward the high order end of this byte, and from low order
        to high order in subsequent bytes.

        If the returned output quantity is not a multiple of eight, the
        remaining bits in the final data byte will be padded with zeros (toward
        the high order end of the byte). The Byte Count field specifies the
        quantity of complete bytes of data."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.1


    The request PDU with function code 01 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x01\x00d\x00\x03')
        (1, 100, 3)

    The reponse PDU varies in length, depending on the request. Each 8 coils
    require 1 byte. The amount of bytes needed represent status of the coils to
    can be calculated with: bytes = round(quantity / 8) + 1. This response
    contains (3 / 8 + 1) = 1 byte to describe the status of the coils. The
    structure of a compleet response PDU looks like this:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Byte count       1
        Coil status      n
        ================ ===============

    Assume the status of 102 is 0, 101 is 1 and 100 is also 1. This is binary
    011 which is decimal 3.

    The PDU can packed like this::

        >>> struct.pack('>BBB', function_code, byte_count, 3)
        b'\x01\x01\x03'

    """
    function_code = READ_COILS
    max_quantity = 2000

    def __init__(self, starting_address, quantity):
        self.format_character = conf.SINGLE_BIT_VALUE_FORMAT_CHARACTER
        ReadFunction.__init__(self, starting_address, quantity)


class ReadDiscreteInputs(ReadFunction, SingleBitResponse):
    """ Implement Modbus function code 02.

        "This function code is used to read from 1 to 2000 contiguous status of
        discrete inputs in a remote device. The Request PDU specifies the
        starting address, i.e. the address of the first input specified, and the
        number of inputs. In the PDU Discrete Inputs are addressed starting at
        zero.  Therefore Discrete inputs numbered 1-16 are addressed as 0-15.

        The discrete inputs in the response message are packed as one input per
        bit of the data field.  Status is indicated as 1= ON; 0= OFF. The LSB of
        the first data byte contains the input addressed in the query. The other
        inputs follow toward the high order end of this byte, and from low order
        to high order in subsequent bytes.

        If the returned input quantity is not a multiple of eight, the remaining
        bits in the final d ata byte will be padded with zeros (toward the high
        order end of the byte). The Byte Count field specifies the quantity of
        complete bytes of data."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.2

    The request PDU with function code 02 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x02\x00d\x00\x03')
        (2, 100, 3)

    The reponse PDU varies in length, depending on the request. 8 inputs
    require 1 byte. The amount of bytes needed represent status of the inputs
    to can be calculated with: bytes = round(quantity / 8) + 1. This response
    contains (3 / 8 + 1) = 1 byte to describe the status of the inputs. The
    structure of a compleet response PDU looks like this:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Byte count       1
        Coil status      n
        ================ ===============

    Assume the status of 102 is 0, 101 is 1 and 100 is also 1. This is binary
    011 which is decimal 3.

    The PDU can packed like this::

        >>> struct.pack('>BBB', function_code, byte_count, 3)
        b'\x02\x01\x03'

    """
    function_code = READ_DISCRETE_INPUTS
    max_quantity = 2000

    def __init__(self, starting_address, quantity):
        self.format_character = conf.SINGLE_BIT_VALUE_FORMAT_CHARACTER
        ReadFunction.__init__(self, starting_address, quantity)


class ReadHoldingRegisters(ReadFunction, MultiBitResponse):
    """ Implement Modbus function code 03.

        "This function code is used to read the contents of a contiguous block
        of holding registers in a remote device. The Request PDU specifies the
        starting register address and the number of registers. In the PDU
        Registers are addressed starting at zero. Therefore registers numbered
        1-16 are addressed as 0-15.

        The register data in the response message are packed as two bytes per
        register, with the binary contents right justified within each byte. For
        each register, the first byte contains the high order bits and the
        second contains the low order bits."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.3

    The request PDU with function code 03 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x03\x00d\x00\x03')
        (3, 100, 3)

    The reponse PDU varies in length, depending on the request. By default,
    holding registers are 16 bit (2 bytes) values. So values of 3 holding
    registers is expressed in 2 * 3 = 6 bytes.

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Byte count       1
        Register values  Quantity * 2
        ================ ===============

    Assume the value of 100 is 8, 101 is 0 and 102 is also 15.

    The PDU can packed like this::

        >>> data = [8, 0, 15]
        >>> struct.pack('>BBHHH', function_code, len(data) * 2, *data)
        '\x03\x06\x00\x08\x00\x00\x00\x0f'

    """
    function_code = READ_HOLDING_REGISTERS
    max_quantity = 0x007D

    def __init__(self, starting_address, quantity):
        self.format_character = conf.MULTI_BIT_VALUE_FORMAT_CHARACTER
        ReadFunction.__init__(self, starting_address, quantity)


class ReadInputRegisters(ReadFunction, MultiBitResponse):
    """ Implement Modbus function code 04.

        "This function code is used to read from 1 to 125 contiguous input
        registers in a remote device. The Request PDU specifies the starting
        register address and the number of registers. In the PDU Registers are
        addressed starting at zero. Therefore input registers numbered 1-16 are
        addressed as 0-15.

        The register data in the response message are packed as two bytes per
        register, with the binary contents right justified within each byte.
        For each register, the first byte contains the high order bits and the
        second contains the low order bits."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.4

    The request PDU with function code 04 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x04\x00d\x00\x03')
        (4, 100, 3)

    The reponse PDU varies in length, depending on the request. By default,
    holding registers are 16 bit (2 bytes) values. So values of 3 holding
    registers is expressed in 2 * 3 = 6 bytes.

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Byte count       1
        Register values  Quantity * 2
        ================ ===============

    Assume the value of 100 is 8, 101 is 0 and 102 is also 15.

    The PDU can packed like this::

        >>> data = [8, 0, 15]
        >>> struct.pack('>BBHHH', function_code, len(data) * 2, *data)
        '\x04\x06\x00\x08\x00\x00\x00\x0f'

    """
    function_code = READ_INPUT_REGISTERS
    max_quantity = 0x007D

    def __init__(self, starting_address, quantity):
        self.format_character = conf.MULTI_BIT_VALUE_FORMAT_CHARACTER
        ReadFunction.__init__(self, starting_address, quantity)


class WriteSingleCoil(WriteSingleValueFunction):
    """ Implement Modbus function code 05.

        "This function code is used to write a single output to either ON or OFF
        in a remote device. The requested ON/OFF state is specified by a
        constant in the request data field. A value of FF 00 hex requests the
        output to be ON.  A value of 00 00 requests it to be OFF. All other
        values are illegal and will not affect the output.

        The Request PDU specifies the address of the coil to be forced. Coils
        are addressed starting at zero. Therefore coil numbered 1 is addressed
        as 0.  The requested ON/OFF state is specified by a constant in the Coil
        Value field. A value of 0XFF00 requests the coil to be ON. A value of
        0X0000 requests the coil to be off. All other values are illegal and
        will not affect the coil.

        The normal response is an echo of the request, returned after the coil
        state has been written."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.5

    The request PDU with function code 05 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Address          2
        Value            2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x05\x00d\xFF\x00')
        (5, 100, 65280)

    The reponse PDU is a copy of the request PDU.

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Address          2
        Value            2
        ================ ===============

    """
    function_code = WRITE_SINGLE_COIL
    format_character = 'H'

    def __init__(self, address, value):
        WriteSingleValueFunction.__init__(self, address, value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """ Validate if value is 0 or 0xFF00. """
        if value not in [0, 0xFF00]:
            raise IllegalDataValueError

        self._value = value

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A response PDU.
        """
        _, address, value = \
            struct.unpack('>BH' + cls.format_character, pdu)

        return cls(address, value)


class WriteSingleRegister(WriteSingleValueFunction):
    """ Implement Modbus function code 06.

        "This function code is used to write a single holding register in a
        remote device. The Request PDU specifies the address of the register to
        be written. Registers are addressed starting at zero. Therefore register
        numbered 1 is addressed as 0. The normal response is an echo of the
        request, returned after the register contents have been written."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.6

    The request PDU with function code 06 must be 5 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Address          2
        Value            2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHH', b'\x06\x00d\x00\x03')
        (6, 100, 3)

    The reponse PDU is a copy of the request PDU.

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Address          2
        Value            2
        ================ ===============

    """
    function_code = WRITE_SINGLE_REGISTER

    def __init__(self, address, value):
        self.format_character = conf.MULTI_BIT_VALUE_FORMAT_CHARACTER
        WriteSingleValueFunction.__init__(self, address, value)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        """ Validate if value is in range of 0 between 0xFFFF (which is maximum
        a number a 16 bit number can be).
        """
        try:
            struct.pack('>' + self.format_character, value)
        except struct.error:
            raise IllegalDataValueError

        self._value = value

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A response PDU.
        """
        _, address, value = \
            struct.unpack('>BH' + conf.MULTI_BIT_VALUE_FORMAT_CHARACTER, pdu)

        return cls(address, value)


class WriteMultipleCoils(WriteMultipleValueFunction):
    """ Implement Modbus function 15 (0x0F) Write Multiple Coils.

        "This function code is used to force each coil in a sequence of coils to
        either ON or OFF in a remote device. The Request PDU specifies the coil
        references to be forced. Coils are addressed starting at zero. Therefore
        coil numbered 1 is addressed as 0.

        The requested ON/OFF states are specified by contents of the request
        data field. A logical '1' in a bit position of the field requests the
        corresponding output to be ON. A logical '0' requests it to be OFF.

        The normal response returns the function code, starting address, and
        quantity of coils forced."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.11

    The request PDU with function code 15 must be at least 7 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting Address 2
        Quantity         2
        Byte count       1
        Value            n
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHHBB', b'\x0f\x00d\x00\x03\x01\x05')
        (16, 100, 3, 1, 5)

    The reponse PDU is 5 bytes and contains following structure:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    """
    function_code = WRITE_MULTIPLE_COILS

    def __init__(self, starting_address, quantity, byte_count, values):
        if not(1 <= quantity <= 0x7B0):
            raise IllegalDataValueError('Quantify field of request must be a '
                                        'value between 0 and '
                                        '{0}.'.format(0x7B0))

        expected_byte_count = ceil(len(values) / 8)

        if not(expected_byte_count == byte_count):
            raise IllegalDataValueError('Byte count is not correct. It is {0},'
                                        'but should be {1}.'
                                        .format(byte_count,
                                                expected_byte_count))

        self.format_character = conf.SINGLE_BIT_VALUE_FORMAT_CHARACTER
        WriteMultipleValueFunction.__init__(self, starting_address, values)

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        This method requires some clarification regarding the unpacking of
        the status that are being passed to the callbacks.

        A coil status can be 0 or 1. The request PDU contains at least 1 byte,
        representing the status for 1 to 8 coils.

        Assume a request with starting address 100, quantity set to 3 and the
        value byte is 6. 0b110 is the binary reprensention of decimal 6. The
        Least Significant Bit (LSB) is status of coil with starting address. So
        status of coil 100 is 0, status of coil 101 is 1 and status of coil 102
        is 1 too.

        coil address  102     101     100
                        1       1       0

        Again, assume starting address 100 and  byte value is 6. But now
        quantity is 4. So the value byte is addressing 4 coils. The binary
        representation of 6 is now 0b0110. LSB again is 0, meaning status of
        coil 100 is 0. Status of 101 and 102 is 1, like in the previous example.
        Status of coil 104 is 0.

        coil address  104     102     101     100
                        0       1       1       0


        In short: the binary representation of the byte value is in reverse
        mapped to the coil addresses. In table below you can see some more
        examples.

        #  quantity value binary representation | 102 101 100
        == ======== ===== ===================== | === === ===
        01 1        0     0b0                      -   -   0
        02 1        1     0b1                      -   -   1
        03 2        0     0b00                     -   0   0
        04 2        1     0b01                     -   0   1
        05 2        2     0b10                     -   1   0
        06 2        3     0b11                     -   1   1
        07 3        0     0b000                    0   0   0
        08 3        1     0b001                    0   0   1
        09 3        2     0b010                    0   1   0
        10 3        3     0b011                    0   1   1
        11 3        4     0b100                    1   0   0
        12 3        5     0b101                    1   0   1
        13 3        6     0b110                    1   1   0
        14 3        7     0b111                    1   1   1

        :param pdu: A request PDU.
        """
        _, starting_address, quantity, byte_count = \
            struct.unpack('>BHHB', pdu[:6])

        fmt = '>' + (conf.SINGLE_BIT_VALUE_FORMAT_CHARACTER * byte_count)
        values = struct.unpack(fmt, pdu[6:])

        res = list()

        for i, value in enumerate(values):
            padding = 8 if (quantity - (8 * i)) // 8 > 0 else quantity % 8
            fmt = '{{0:0{padding}b}}'.format(padding=padding)

            # Create binary representation of integer, convert it to a list
            # and reverse the list.
            res = res + [int(i) for i in fmt.format(value)][::-1]

        return cls(starting_address, quantity, byte_count, res)


class WriteMultipleRegisters(WriteMultipleValueFunction):
    """ Implement Modbus function 16 (0x10) Write Multiple Registers.

        "This function code is used to write a block of contiguous registers (1
        to 123 registers) in a remote device.

        The requested written values are specified in the request data field.
        Data is packed as two bytes per register.

        The normal response returns the function code, starting address, and
        quantity of registers written."

        -- MODBUS Application Protocol Specification V1.1b3, chapter 6.12

    The request PDU with function code 16 must be at least 8 bytes:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting Address 2
        Quantity         2
        Byte count       1
        Value            Quantity * 2
        ================ ===============

    The PDU can unpacked to this::

        >>> struct.unpack('>BHHBH', b'\x10\x00d\x00\x01\x02\x00\x05')
        (16, 100, 1, 2, 5)

    The reponse PDU is 5 bytes and contains following structure:

        ================ ===============
        Field            Length (bytes)
        ================ ===============
        Function code    1
        Starting address 2
        Quantity         2
        ================ ===============

    """
    function_code = WRITE_MULTIPLE_REGISTERS

    def __init__(self, starting_address, quantity, byte_count, values):
        if not(1 <= quantity <= 0x7B):
            raise IllegalDataValueError('Quantify field of request must be a '
                                        'value between 0 and '
                                        '{0}.'.format(0x7B0))

        # Values are 16 bit, so each value takes up 2 bytes.
        if byte_count != (len(values) * 2):
            raise IllegalDataValueError('Byte count is not correct. It is {0},'
                                        'but should be {1}.'
                                        .format(byte_count, len(values)))

        self.format_character = conf.MULTI_BIT_VALUE_FORMAT_CHARACTER
        WriteMultipleValueFunction.__init__(self, starting_address, values)

    @classmethod
    def create_from_request_pdu(cls, pdu):
        """ Create instance from request PDU.

        :param pdu: A request PDU.
        :return: Instance of this class.
        """
        _, starting_address, quantity, byte_count = \
            struct.unpack('>BHHB', pdu[:6])

        # Values are 16 bit, so each value takes up 2 bytes.
        fmt = '>' + (conf.MULTI_BIT_VALUE_FORMAT_CHARACTER * int((byte_count / 2)))

        values = list(struct.unpack(fmt, pdu[6:]))
        return cls(starting_address, quantity, byte_count, values)


function_code_to_function_map = {
    READ_COILS: ReadCoils,
    READ_DISCRETE_INPUTS: ReadDiscreteInputs,
    READ_HOLDING_REGISTERS: ReadHoldingRegisters,
    READ_INPUT_REGISTERS: ReadInputRegisters,
    WRITE_SINGLE_COIL: WriteSingleCoil,
    WRITE_SINGLE_REGISTER: WriteSingleRegister,
    WRITE_MULTIPLE_COILS: WriteMultipleCoils,
    WRITE_MULTIPLE_REGISTERS: WriteMultipleRegisters,
}
