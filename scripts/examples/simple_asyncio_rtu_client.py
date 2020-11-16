#!/usr/bin/env python
# scripts/example/simple_async_rtu_client.py
import asyncio

from serial_asyncio import open_serial_connection

from umodbus.client.serial import rtu
from umodbus.client.serial.asynch import send_message


async def main():
    reader, writer = await open_serial_connection(url='/dev/ttyS1', timeout=1)

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus TCP/IP.
    message = rtu.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

    # Response depends on Modbus function code. This particular returns the
    # amount of coils written, in this case it is.
    response = await send_message(message, reader, writer)

    writer.close()
    await writer.wait_closed()


asyncio.run(main())
