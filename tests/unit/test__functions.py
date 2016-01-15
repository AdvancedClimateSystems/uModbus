import struct
import pytest

from umodbus.exceptions import (IllegalFunctionError, IllegalDataAddressError,
                                IllegalDataValueError,
                                ServerDeviceFailureError, AcknowledgeError,
                                ServerDeviceBusyError, MemoryParityError,
                                GatewayPathUnavailableError,
                                GatewayTargetDeviceFailedToRespondError)
from umodbus._functions import (create_function_from_response_pdu, ReadCoils,
                                ReadDiscreteInputs, ReadHoldingRegisters,
                                ReadInputRegisters)


def test_create_function_from_response_pdu():
    resp_pdu = struct.pack('>BBB', 1, 1, 3)

    assert isinstance(create_function_from_response_pdu(resp_pdu, 3),
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

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BBBB', 2, 2, 170, 2)
        read_coils = ReadCoils.create_from_response_pdu(resp_pdu, 10)

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

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BBB', 1, 1, 3)

        read_discrete_inputs = \
            ReadDiscreteInputs.create_from_response_pdu(resp_pdu, 3)

        assert read_discrete_inputs.data == [1, 1, 0]


class TestReadHoldingRegisters:
    @pytest.fixture
    def read_holding_registers(self):
        """ Return instance of ReadCoils. """
        read_holding_registers = ReadHoldingRegisters()
        read_holding_registers.starting_address = 5
        read_holding_registers.quantity = 6

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

    def test_request_pdu(self, read_holding_registers):
        """ Test if correct request PDU is build. """
        assert read_holding_registers.request_pdu == \
            struct.pack('>BHH', 3, 5, 6)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BBHHH', 3, 6, 3, 1337, 28490)

        read_holding_registers = \
            ReadHoldingRegisters.create_from_response_pdu(resp_pdu, 3)

        assert read_holding_registers.data == [3, 1337, 28490]


class TestReadInputRegisters:
    @pytest.fixture
    def read_input_registers(self):
        """ Return instance of ReadInputRegisters. """
        read_input_registers = ReadInputRegisters()
        read_input_registers.starting_address = 1
        read_input_registers.quantity = 6

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
            struct.pack('>BHH', 4, 1, 6)

    def test_create_from_response_pdu(self):
        """ Test if function instance is created correctly from response PDU.
        """
        resp_pdu = struct.pack('>BBHH', 4, 4, 9209, 230)

        read_input_registers = \
            ReadInputRegisters.create_from_response_pdu(resp_pdu, 2)

        assert read_input_registers.data == [9209, 230]
