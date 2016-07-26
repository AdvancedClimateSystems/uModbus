import struct
import pytest

try:
    # Mock has been added to stdlib in Python 3.3.
    from unittest.mock import MagicMock, call
except ImportError:
    from mock import MagicMock, call

from umodbus.route import Map
from umodbus.exceptions import (IllegalFunctionError, IllegalDataAddressError,
                                IllegalDataValueError,
                                ServerDeviceFailureError, AcknowledgeError,
                                ServerDeviceBusyError, MemoryParityError,
                                GatewayPathUnavailableError,
                                GatewayTargetDeviceFailedToRespondError)
from umodbus.functions import (create_function_from_response_pdu,
                               create_function_from_request_pdu, ReadCoils,
                               ReadDiscreteInputs, ReadHoldingRegisters,
                               ReadInputRegisters, WriteSingleCoil,
                               WriteSingleRegister, WriteMultipleCoils,
                               WriteMultipleRegisters)


@pytest.fixture
def read_coils():
    function_code = 1
    starting_address = 100
    quantity = 3

    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    return ReadCoils.create_from_request_pdu(pdu)


@pytest.fixture
def read_holding_registers():
    function_code = 3
    starting_address = 100
    quantity = 3

    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    return ReadHoldingRegisters.create_from_request_pdu(pdu)


@pytest.fixture
def write_single_coil():
    function_code = 5
    address = 100
    value = 0xFF00

    pdu = struct.pack('>BHH', function_code, address, value)

    return WriteSingleCoil.create_from_request_pdu(pdu)


@pytest.fixture
def write_multiple_coils():
    function_code = 15
    starting_address = 100
    quantity = 10
    byte_count = 2
    values = (2, 1)

    pdu = struct.pack('>BHHBBB', function_code, starting_address, quantity,
                      byte_count, *values)
    return WriteMultipleCoils.create_from_request_pdu(pdu)


@pytest.fixture
def write_multiple_registers():
    function_code = 16
    starting_address = 100
    quantity = 3
    byte_count = 6
    values = [1337, 15, 128]

    pdu = struct.pack('>BHHBHHH', function_code, starting_address, quantity,
                      byte_count, *values)
    return WriteMultipleRegisters.create_from_request_pdu(pdu)


@pytest.fixture
def route_map():
    return Map()


@pytest.mark.parametrize('pdu,cls', [
    (b'\x01\x00d\x00\x03', ReadCoils),
    (b'\x02\x00d\x00\x03', ReadDiscreteInputs),
    (b'\x03\x00d\x00\x03', ReadHoldingRegisters),
    (b'\x04\x00d\x00\x03', ReadInputRegisters),
    (b'\x05\x00d\x00\x00', WriteSingleCoil),
    (b'\x06\x00d\x00\x00', WriteSingleRegister),
    (b'\x0f\x00d\x00\x03\x01\x04', WriteMultipleCoils),
    (b'\x10\x00d\x00\x01\x02\x00\x04', WriteMultipleRegisters),
])
def test_create_function_from_request_pdu(pdu, cls):
    assert isinstance(create_function_from_request_pdu(pdu), cls)


def test_create_function_from_request_pdu_raising_illegal_function_error():
    """ Calling function with PDU containing invalid function code should result
    in an IllegalFunctionError.
    """
    with pytest.raises(IllegalFunctionError):
        create_function_from_request_pdu(b'\x00')


class TestReadCoils:
    def test_class_attributes(self):
        assert ReadCoils.function_code == 1
        assert ReadCoils.max_quantity == 2000


class TestReadDiscreteInputs:
    def test_class_attributes(self):
        assert ReadDiscreteInputs.function_code == 2
        assert ReadDiscreteInputs.max_quantity == 2000


class TestReadHoldingRegisters:
    def test_class_attributes(self):
        assert ReadHoldingRegisters.function_code == 3
        assert ReadHoldingRegisters.max_quantity == 125


class TestReadInputRegisters:
    def test_class_attributes(self):
        assert ReadInputRegisters.function_code == 4
        assert ReadInputRegisters.max_quantity == 125


class TestWriteSingleCoil:
    @pytest.mark.parametrize('value', [
        0,
        0xFF00,
    ])
    def test_write_valid_status(self, value):
        """ Call should not raise exception. """
        write_single_coil = WriteSingleCoil(100, value)
        assert write_single_coil.value == value

    def test_write_invalid_status(self):
        """ Creating instance with invalid value should raise exception. """
        with pytest.raises(IllegalDataValueError):
            WriteSingleCoil(100, 5)


class TestWriteSingleRegister:
    @pytest.mark.parametrize('value', [
        0,
        32000,
        0xFFFF,
    ])
    def test_write_valid_value(self, value):
        """ Call should not raise exception. """
        write_single_register = WriteSingleRegister(100, value)
        assert write_single_register.value == value

    @pytest.mark.parametrize('value', [
        -1,
        0xFFFF + 1,
    ])
    def test_write_invalid_value(self, value):
        """ Creating instance with invalid values should raise exception. """
        with pytest.raises(IllegalDataValueError):
            WriteSingleRegister(100, value)


class TestWriteMultipleCoils:
    def test_create_from_request_pdu(self, write_multiple_coils):
        assert write_multiple_coils.function_code == 15
        assert write_multiple_coils.starting_address == 100
        assert write_multiple_coils.values == [0, 1, 0, 0, 0, 0, 0, 0, 1, 0]

    @pytest.mark.parametrize('quantity', [
        0,
        0x7B0 + 1,
    ])
    def test_create_instance_with_invalid_quantity(self, quantity):
        """ Creating instance with invalid quantity should raise exception. """
        with pytest.raises(IllegalDataValueError):
            WriteMultipleCoils(100, quantity, 1, [1])

    def test_create_instance_with_invalid_byte_count(self):
        """ Creating instance with invalid byte count should raise exception.
        """
        with pytest.raises(IllegalDataValueError):
            WriteMultipleCoils(100, 1, 2, [1])


class TestWriteMultipleRegister:
    def test_create_from_request_pdu(self, write_multiple_registers):
        assert write_multiple_registers.function_code == 16
        assert write_multiple_registers.starting_address == 100
        assert write_multiple_registers.values == [1337, 15, 128]

    def test_create_instance_with_invalid_quantity(self, write_multiple_registers):
        """ Creating instance with invalid quantity should raise exception. """
        with pytest.raises(IllegalDataValueError):
            write_multiple_registers.values = []


def test_create_function_from_response_pdu():
    read_coils = ReadCoils()
    read_coils.starting_address = 1
    read_coils.quantity = 9

    req_pdu = read_coils.request_pdu
    resp_pdu = struct.pack('>BBB', 1, 1, 3)

    assert isinstance(create_function_from_response_pdu(resp_pdu, req_pdu),
                      ReadCoils)


@pytest.mark.parametrize('error_code, exception_class', [
    (1, IllegalFunctionError),
    (2, IllegalDataAddressError),
    (3, IllegalDataValueError),
    (4, ServerDeviceFailureError),
    (5, AcknowledgeError),
    (6, ServerDeviceBusyError),
    (8, MemoryParityError),
    (11, GatewayPathUnavailableError),
    (12, GatewayTargetDeviceFailedToRespondError),
])
def test_create_from_response_pdu_raising_exception(error_code,
                                                    exception_class):
    """ Test if correct exception is raied when response PDU contains error
    response.
    """
    resp_pdu = struct.pack('>BB', 81, error_code)

    with pytest.raises(exception_class):
        create_function_from_response_pdu(resp_pdu)


class TestReadCoils:
    @pytest.fixture
    def read_coils(self):
        """ Return instance of ReadCoils. """
        read_coils = ReadCoils()
        read_coils.starting_address = 1
        read_coils.quantity = 9

        return read_coils

    def test_function_code(self, read_coils):
        """ Test if function_code is correct. """
        assert read_coils.function_code == 1

    @pytest.mark.parametrize('quantity', [
        0,
        2001,
    ])
    def test_set_quantity_raising_illegal_data_value_error(self, read_coils,
                                                           quantity):
        """ Test if exception is raised when number of coils to read is
        invalid.
        """
        with pytest.raises(IllegalDataValueError):
            read_coils.quantity = quantity

    def test_request_pdu(self, read_coils):
        """ Test if correct request PDU is build. """
        assert read_coils.request_pdu == struct.pack('>BHH', 1, 1, 9)

    def test_create_from_response_pdu(self, read_coils):
        """ Test if function instance is created correctly from response PDU.
        """
        req_pdu = read_coils.request_pdu
        resp_pdu = struct.pack('>BBBB', 2, 2, 170, 2)

        read_coils = ReadCoils.create_from_response_pdu(resp_pdu, req_pdu)

        assert read_coils.data == [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]


class TestReadDiscreteInputs:
    @pytest.fixture
    def read_discrete_inputs(self):
        """ Return instance of ReadCoils. """
        read_discrete_inputs = ReadDiscreteInputs()
        read_discrete_inputs.starting_address = 8
        read_discrete_inputs.quantity = 2

        return read_discrete_inputs

    def test_function_code(self, read_discrete_inputs):
        """ Test if function_code is correct. """
        assert read_discrete_inputs.function_code == 2

    @pytest.mark.parametrize('quantity', [
        0,
        2001,
    ])
    def test_set_quantity_raising_illegal_data_value_error(self,
                                                           read_discrete_inputs,  # NOQA
                                                           quantity):
        """ Test if exception is raised when number of coils to read is
        invalid.
        """
        with pytest.raises(IllegalDataValueError):
            read_discrete_inputs.quantity = quantity

    def test_request_pdu(self, read_discrete_inputs):
        """ Test if correct request PDU is build. """
        assert read_discrete_inputs.request_pdu == struct.pack('>BHH', 2, 8, 2)

    def test_create_from_response_pdu(self, read_discrete_inputs):
        """ Test if function instance is created correctly from response PDU.
        """
        req_pdu = read_discrete_inputs.request_pdu
        resp_pdu = struct.pack('>BBB', 1, 1, 3)

        read_discrete_inputs = \
            ReadDiscreteInputs.create_from_response_pdu(resp_pdu, req_pdu)

        assert read_discrete_inputs.data == [1, 1]


class TestReadHoldingRegisters:
    @pytest.fixture
    def read_holding_registers(self):
        """ Return instance of ReadCoils. """
        read_holding_registers = ReadHoldingRegisters()
        read_holding_registers.starting_address = 5
        read_holding_registers.quantity = 3

        return read_holding_registers

    def test_function_code(self, read_holding_registers):
        """ Test if function_code is correct. """
        assert read_holding_registers.function_code == 3

    @pytest.mark.parametrize('quantity', [
        0,
        0x007D + 1,
    ])
    def test_set_quantity_raising_illegal_data_value_error(self,
                                                           read_holding_registers,  # NOQA
                                                           quantity):
        """ Test if exception is raised when number of registers to read is
        invalid.
        """
        with pytest.raises(IllegalDataValueError):
            read_holding_registers.quantity = quantity


    def test_create_from_response_pdu(self, read_holding_registers):
        """ Test if function instance is created correctly from response PDU.
        """
        req_pdu = read_holding_registers.request_pdu
        resp_pdu = struct.pack('>BBHHH', 3, 6, 3, 1337, 28490)

        read_holding_registers = \
            ReadHoldingRegisters.create_from_response_pdu(resp_pdu, req_pdu)

        assert read_holding_registers.data == [3, 1337, 28490]


class TestReadInputRegisters:
    @pytest.fixture
    def read_input_registers(self):
        """ Return instance of ReadInputRegisters. """
        read_input_registers = ReadInputRegisters()
        read_input_registers.starting_address = 1
        read_input_registers.quantity = 2

        return read_input_registers

    def test_function_code(self, read_input_registers):
        """ Test if function_code is correct. """
        assert read_input_registers.function_code == 4

    @pytest.mark.parametrize('quantity', [
        0,
        0x007D + 1,
    ])
    def test_set_quantity_raising_illegal_data_value_error(self,
                                                           read_input_registers,  # NOQA
                                                           quantity):
        """ Test if exception is raised when number of registers to read is
        invalid.
        """
        with pytest.raises(IllegalDataValueError):
            read_input_registers.quantity = quantity

    def test_request_pdu(self, read_input_registers):
        """ Test if correct request PDU is build. """
        assert read_input_registers.request_pdu == \
            struct.pack('>BHH', 4, 1, 2)

    def test_create_from_response_pdu(self, read_input_registers):
        """ Test if function instance is created correctly from response PDU.
        """
        req_pdu = read_input_registers.request_pdu
        resp_pdu = struct.pack('>BBHH', 4, 4, 9209, 230)

        read_input_registers = \
            ReadInputRegisters.create_from_response_pdu(resp_pdu, req_pdu)

        assert read_input_registers.data == [9209, 230]


class TestWriteSingleCoil:

    @pytest.fixture
    def write_single_coil(self):
        """ Return instance of WriteSingleCoil. """
        write_single_coil = WriteSingleCoil()
        write_single_coil.address = 4
        write_single_coil.value = 0xFF00

        return write_single_coil

    def test_function_code(self, write_single_coil):
        """ Test if function_code is correct. """
        assert write_single_coil.function_code == 5

    def test_set_value_raising_illegal_data_value_error(self,
                                                        write_single_coil):
        """ Test if exception is raised when value is not valid. """
        with pytest.raises(IllegalDataValueError):
            write_single_coil.value = 2

    def test_request_pdu(self, write_single_coil):
        """ Test if correct request PDU is build. """
        assert write_single_coil.request_pdu == \
            struct.pack('>BHH', 5, 4, 0xFF00)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BHH', 5, 4, 0xFF00)

        write_single_coil = WriteSingleCoil.create_from_response_pdu(resp_pdu)

        assert write_single_coil.data == 0xFF00


class TestWriteSingleRegister:

    @pytest.fixture
    def write_single_register(self):
        """ Return instance of WriteSingleRegister. """
        write_single_register = WriteSingleRegister()
        write_single_register.address = 4
        write_single_register.value = 0xFF00

        return write_single_register

    def test_function_code(self, write_single_register):
        """ Test if function_code is correct. """
        assert write_single_register.function_code == 6

    def test_set_value_raising_illegal_data_value_error(self,
                                                        write_single_register):
        """ Test if exception is raised when value is not valid. """
        with pytest.raises(IllegalDataValueError):
            write_single_register.value = 0xFFFF0

    def test_request_pdu(self, write_single_register):
        """ Test if correct request PDU is build. """
        assert write_single_register.request_pdu == \
            struct.pack('>BHH', 6, 4, 0xFF00)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BHH', 6, 4, 1337)

        write_single_register = \
            WriteSingleRegister.create_from_response_pdu(resp_pdu)

        assert write_single_register.data == 1337


class TestWriteMultipleCoils:

    @pytest.fixture
    def write_multiple_coils(self):
        """ Return instance of WriteSingleRegister. """
        write_multiple_coils = WriteMultipleCoils()
        write_multiple_coils.starting_address = 8
        write_multiple_coils.values = [1, 1, 0]

        return write_multiple_coils

    def test_function_code(self, write_multiple_coils):
        """ Test if function_code is correct. """
        assert write_multiple_coils.function_code == 15

    def test_set_value_raising_illegal_data_value_error(self,
                                                        write_multiple_coils):
        """ Test if exception is raised when value is not valid. """
        with pytest.raises(IllegalDataValueError):
            write_multiple_coils.values = [1, 4]

        with pytest.raises(IllegalDataValueError):
            write_multiple_coils.values = []

    def test_request_pdu(self, write_multiple_coils):
        """ Test if correct request PDU is build. """
        assert write_multiple_coils.request_pdu == \
            struct.pack('>BHHBB', 15, 8, 3, 1, 3)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BHH', 6, 4, 3)

        write_multiple_coils = \
            WriteMultipleCoils.create_from_response_pdu(resp_pdu)

        assert write_multiple_coils.data == 3


class TestWriteMultipleRegisters:

    @pytest.fixture
    def write_multiple_registers(self):
        """ Return instance of WriteSingleRegister. """
        write_multiple_registers = WriteMultipleRegisters()
        write_multiple_registers.starting_address = 13
        write_multiple_registers.values = [484, 1337]

        return write_multiple_registers

    def test_function_code(self, write_multiple_registers):
        """ Test if function_code is correct. """
        assert write_multiple_registers.function_code == 16

    def test_set_value_raising_illegal_data_value_error(self,
                                                        write_multiple_registers):  # NOQA
        """ Test if exception is raised when value is not valid. """
        with pytest.raises(IllegalDataValueError):
            write_multiple_registers.values = []

    def test_request_pdu(self, write_multiple_registers):
        """ Test if correct request PDU is build. """
        assert write_multiple_registers.request_pdu == \
            struct.pack('>BHHBHH', 16, 13, 2, 4, 484, 1337)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BHH', 6, 4, 3)

        write_multiple_registers = \
            WriteMultipleRegisters.create_from_response_pdu(resp_pdu)

        assert write_multiple_registers.data == 3
