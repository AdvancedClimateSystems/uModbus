import pytest
import struct

from modbus.route import Map
from modbus.functions import (function_factory, ReadCoils,
                              ReadDiscreteInputs, ReadInputRegisters,
                              ReadHoldingRegisters, WriteSingleCoil)
from modbus.exceptions import IllegalDataValueError, IllegalDataAddressError


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
def single_bit_enpoint():
    """ Return endpoint for Modbus request acting on single bit values,
    like Modbus function codes 01 an 02.
    """
    def endpoint(slave_id, address):
        return address % 2


@pytest.fixture
def route_map():
    return Map()


@pytest.mark.parametrize('pdu,cls', [
    (b'\x01\x00d\x00\x03', ReadCoils),
    (b'\x02\x00d\x00\x03', ReadDiscreteInputs),
    (b'\x03\x00d\x00\x03', ReadHoldingRegisters),
    (b'\x04\x00d\x00\x03', ReadInputRegisters),
    (b'\x05\x00d\x00\x00', WriteSingleCoil),

])
def test_function_factory(pdu, cls):
    assert isinstance(function_factory(pdu), cls)


def test_caching_of_function_factory():
    """ Equal calls to :meth:`function_factory` should return same response.
    """
    function_code = 1
    starting_address = 100
    quantity = 3

    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    # Call method twice, both with same input...
    function_1 = function_factory(pdu)
    function_2 = function_factory(pdu)

    # ...output should be the same.
    assert id(function_1) == id(function_2)

    starting_address = 101
    pdu = struct.pack('>BHH', function_code, starting_address, quantity)

    # But when called with different pdu...
    function_3 = function_factory(pdu)

    # ...output should not be the same as previous calls.
    assert id(function_1) is not id(function_3)


class TestReadFunction:
    def test_create_from_request_pdu(self):
        """ Call should return instance with correct attributes and vaules. """
        function_code = 1
        starting_address = 100
        quantity = 3

        pdu = struct.pack('>BHH', function_code, starting_address, quantity)

        function = ReadCoils.create_from_request_pdu(pdu)
        assert function.starting_address == starting_address
        assert function.quantity == quantity

    def test_create_from_request_pdu_raising_illegal_data_value_error(self):
        function_code = ReadCoils.function_code
        address = 100
        quantity = ReadCoils.max_quantity + 1

        pdu = struct.pack('>BHH', function_code, address, quantity)

        with pytest.raises(IllegalDataValueError):
            ReadCoils.create_from_request_pdu(pdu)

    def test_execute(self, read_coils, route_map, monkeypatch):
        """ SingleBitFunction.execute should execute endpoints an return correct
        result.
        """
        def match_mock(*args, **kwargs):
            return lambda slave_id, address: address % 2

        monkeypatch.setattr(route_map, 'match', match_mock)
        assert read_coils.execute(1, route_map) == [0, 1, 0]

    def test_execute_raising_illegal_data_error(self, read_coils, route_map):
        """ When no route is found for request, execute should raise an
        IllegalDataAddressError.
        """
        with pytest.raises(IllegalDataAddressError):
            read_coils.execute(1, route_map)


class TestSingleBitResponse:
    @pytest.mark.parametrize('data,expectation', [
        ([1, 1, 0], b'\x01\x01\x03'),
        ([0, 1, 0, 0, 0, 0, 0, 0, 1], b'\x01\x02\x02\x01'),
    ])
    def test_create_response_pdu(self, read_coils, data, expectation):
        assert read_coils.create_response_pdu(data) == expectation


class TestMultiBitResponse:
    def test_create_response_pdu(self, read_holding_registers):
        assert read_holding_registers.create_response_pdu([0, 1337]) == \
            b'\x03\x04\x00\x00\x059'


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
    @pytest.mark.parametrize('status', [
        0,
        0xFF00,
    ])
    def test_write_valid_status(self, status):
        """ Call should not raise exception. """
        write_single_coil = WriteSingleCoil(100, status)
        assert write_single_coil.value == status

    def test_write_invalid_status(self):
        """ Creating instance with invalid status should raise exception. """
        with pytest.raises(IllegalDataValueError):
            WriteSingleCoil(100, 5)
