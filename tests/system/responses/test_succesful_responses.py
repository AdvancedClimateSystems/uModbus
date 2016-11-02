import pytest

from umodbus import conf
from umodbus.client import tcp


@pytest.fixture(scope='module', autouse=True)
def enable_signed_values(request):
    """ Use signed values when running tests it this module. """
    tmp = conf.SIGNED_VALUES
    conf.SIGNED_VALUES = True

    def fin():
        conf.SIGNED_VALUES = tmp

    request.addfinalizer(fin)


@pytest.mark.parametrize('function', [
    tcp.read_coils,
    tcp.read_discrete_inputs,
])
def test_response_on_single_bit_value_read_requests(sock, function):
    """ Validate response of a succesful Read Coils or Read Discrete Inputs
    request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert tcp.send_message(req_adu, sock) == [0, 1, 0, 1, 0, 1, 0, 1, 0,  1]


@pytest.mark.parametrize('function', [
    tcp.read_holding_registers,
    tcp.read_input_registers,
])
def test_response_on_multi_bit_value_read_requests(sock, function):
    """ Validate response of a succesful Read Holding Registers or Read
    Input Registers request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert tcp.send_message(req_adu, sock) ==\
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]


@pytest.mark.parametrize('function, value', [
    (tcp.write_single_coil, 1),
    (tcp.write_single_register, -1337),
])
def test_response_single_value_write_request(sock, function, value):
    """ Validate responde of succesful Read Single Coil and Read Single
    Register request.
    """
    slave_id, starting_address, value = (1, 0, value)
    req_adu = function(slave_id, starting_address, value)

    assert tcp.send_message(req_adu, sock) == value


@pytest.mark.parametrize('function, values', [
    (tcp.write_multiple_coils, [1, 1]),
    (tcp.write_multiple_registers, [1337, 15]),
])
def test_response_multi_value_write_request(sock, function, values):
    """ Validate response of succesful Write Multiple Coils and Write Multiple
    Registers request.

    Both requests write 2 values, starting address is 0.
    """
    slave_id, starting_address = (1, 0)
    req_adu = function(slave_id, starting_address, values)

    assert tcp.send_message(req_adu, sock) == 2
