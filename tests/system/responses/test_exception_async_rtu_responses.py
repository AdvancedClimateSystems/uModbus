import pytest
import struct
from functools import partial

from ..validators import validate_response_error

from umodbus.client.serial import rtu
from umodbus.client.serial.redundancy_check import (get_crc, validate_crc,
                                                    add_crc, CRCError)


pytestmark = pytest.mark.asyncio


async def req_rep(adu, reader, writer, serial_port):
    writer.write(adu)
    await writer.drain()
    return await reader.read(serial_port.in_waiting)


@pytest.mark.parametrize('function_code, quantity', [
    (1, 0),
    (2, 0),
    (3, 0),
    (4, 0),
    (1, 0x07D0 + 1),
    (2, 0x07D0 + 1),
    (3, 0x007D + 1),
    (4, 0x007D + 1),
])
async def test_request_returning_invalid_data_value_error(
    rtu_server, async_serial_streams, function_code, quantity):
    """ Validate response PDU of request returning exception response with
    error code 3.
    """
    starting_address = 0
    slave_id = 1
    adu = add_crc(struct.pack('>BBHH', slave_id, function_code,
                              starting_address, quantity))

    reader, writer = async_serial_streams
    resp = await req_rep(adu, reader, writer, rtu_server.serial_port)

    validate_crc(resp)
    validate_response_error(resp[:-2], function_code, 3)


@pytest.mark.parametrize('function', [
    (partial(rtu.read_coils, 1, 9, 2)),
    (partial(rtu.read_discrete_inputs, 1, 9, 2)),
    (partial(rtu.read_holding_registers, 1, 9, 2)),
    (partial(rtu.read_input_registers, 1, 9, 2)),
    (partial(rtu.write_single_coil, 1, 11, 0)),
    (partial(rtu.write_single_register, 1, 11, 1337)),
    (partial(rtu.write_multiple_coils, 1, 9, [1, 1])),
    (partial(rtu.write_multiple_registers, 1, 9, [1337, 15])),
])
async def test_request_returning_invalid_data_address_error(rtu_server, async_serial_streams, function):
    """ Validate response PDU of request returning exception response with
    error code 2.
    """
    adu = function()

    function_code = struct.unpack('>B', adu[1:2])[0]

    reader, writer = async_serial_streams
    resp = await req_rep(adu, reader, writer, rtu_server.serial_port)

    validate_crc(resp)
    validate_response_error(resp[:-2], function_code, 2)


@pytest.mark.parametrize('function', [
    (partial(rtu.read_coils, 1, 666, 1)),
    (partial(rtu.read_discrete_inputs, 1, 666, 1)),
    (partial(rtu.read_holding_registers, 1, 666, 1)),
    (partial(rtu.read_input_registers, 1, 666, 1)),
    (partial(rtu.write_single_coil, 1, 666, 0)),
    (partial(rtu.write_single_register, 1, 666, 1337)),
    (partial(rtu.write_multiple_coils, 1, 666, [1])),
    (partial(rtu.write_multiple_registers, 1, 666, [1337])),
])
async def test_request_returning_server_device_failure_error(rtu_server, async_serial_streams, function):
    """ Validate response PDU of request returning exception response with
    error code 4.
    """
    adu = function()

    function_code = struct.unpack('>B', adu[1:2])[0]

    reader, writer = async_serial_streams
    resp = await req_rep(adu, reader, writer, rtu_server.serial_port)

    validate_crc(resp)
    validate_response_error(resp[:-2], function_code, 4)

