import pytest
import platform

from umodbus import conf
from umodbus.client.serial import rtu

implementation = platform.python_implementation()


@pytest.fixture(scope='module', autouse=True)
def enable_signed_values(request):
    """ Use signed values when running tests it this module. """
    tmp = conf.SIGNED_VALUES
    conf.SIGNED_VALUES = True

    def fin():
        conf.SIGNED_VALUES = tmp

    request.addfinalizer(fin)


def send_message(adu, server):
    server.serial_port.write(adu)
    server.serve_once()

    response_adu = server.serial_port.read(server.serial_port.in_waiting)
    return rtu.parse_response_adu(response_adu, adu)


@pytest.mark.parametrize('function', [
    rtu.read_coils,
    rtu.read_discrete_inputs,
])
def test_response_on_single_bit_value_read_requests(rtu_server, function):
    """ Validate response of a succesful Read Coils or Read Discrete Inputs
    request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert send_message(req_adu, rtu_server) == [0, 1, 0, 1, 0, 1, 0, 1, 0,  1]


@pytest.mark.skipif(implementation == 'PyPy',
                    reason='#42 - Some test fail on PyPy')
@pytest.mark.parametrize('function', [
    rtu.read_holding_registers,
    rtu.read_input_registers,
])
def test_response_on_multi_bit_value_read_requests(rtu_server, function):
    """ Validate response of a succesful Read Holding Registers or Read
    Input Registers request.
    """
    slave_id, starting_address, quantity = (1, 0, 10)
    req_adu = function(slave_id, starting_address, quantity)

    assert send_message(req_adu, rtu_server) ==\
        [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]


@pytest.mark.parametrize('function, value', [
    (rtu.write_single_coil, 0),
    (rtu.write_single_register, -1337),
])
def test_response_single_value_write_request(rtu_server, function, value):
    """ Validate responde of succesful Read Single Coil and Read Single
    Register request.
    """
    slave_id, starting_address, quantity = (1, 0, value)
    req_adu = function(slave_id, starting_address, quantity)

    assert send_message(req_adu, rtu_server) == value


@pytest.mark.parametrize('function, values', [
    (rtu.write_multiple_coils, [1, 1]),
    (rtu.write_multiple_registers, [1337, 15]),
])
def test_response_multi_value_write_request(rtu_server, function, values):
    """ Validate response of succesful Write Multiple Coils and Write Multiple
    Registers request.

    Both requests write 2 values, starting address is 0.
    """
    slave_id, starting_address = (1, 0)
    req_adu = function(slave_id, starting_address, values)

    assert send_message(req_adu, rtu_server) == 2
