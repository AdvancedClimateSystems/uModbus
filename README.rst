.. image:: https://travis-ci.org/AdvancedClimateSystems/uModbus.svg
   :target: https://travis-ci.org/AdvancedClimateSystems/uModbus

.. image:: https://coveralls.io/repos/AdvancedClimateSystems/uModbus/badge.svg?service=github
    :target: https://coveralls.io/github/AdvancedClimateSystems/uModbus

.. image:: https://img.shields.io/pypi/v/uModbus.svg
    :target: https://pypi.python.org/pypi/uModbus

.. image:: https://img.shields.io/pypi/pyversions/uModbus.svg
    :target: https://pypi.python.org/pypi/uModbus

uModbus
=======

uModbus or (μModbus) is a pure Python implementation of the Modbus protocol as
described in the `MODBUS Application Protocol Specification V1.1b3`_. uModbus
implements both a Modbus client (both TCP and RTU) and a Modbus server (both
TCP and RTU). The "u" or "μ" in the name comes from the the SI prefix "micro-".
uModbus is very small and lightweight. The source can be found on GitHub_.
Documentation is available at `Read the Docs`_.

Quickstart
----------

Creating a Modbus TCP server is easy:

..
    Because GitHub doesn't support the include directive the source of
    scripts/examples/simple_tcp_server.py has been copied to this file.

.. code:: python

    #!/usr/bin/env python
    # scripts/examples/simple_tcp_server.py
    import logging
    from socketserver import TCPServer
    from collections import defaultdict
    from argparse import ArgumentParser

    from umodbus import conf
    from umodbus.server.tcp import RequestHandler, get_server
    from umodbus.utils import log_to_stream

    # Add stream handler to logger 'uModbus'.
    log_to_stream(level=logging.DEBUG)

    # A very simple data store which maps addresses against their values.
    data_store = defaultdict(int)

    # Enable values to be signed (default is False).
    conf.SIGNED_VALUES = True

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-b", "--bind", default="localhost:502")

    args = parser.parse_args()
    if ":" not in args.bind:
        args.bind += ":502"
    host, port = args.bind.rsplit(":", 1)
    port = int(port)

    TCPServer.allow_reuse_address = True
    try:
        app = get_server(TCPServer, (host, port), RequestHandler)
    except PermissionError:
        print("You don't have permission to bind on {}".format(args.bind))
        print("Hint: try with a different port (ex: --bind localhost:50200)")
        exit(1)

    @app.route(slave_ids=[1], function_codes=[1, 2], addresses=list(range(0, 10)))
    def read_data_store(slave_id, function_code, address):
        """" Return value of address. """
        return data_store[address]


    @app.route(slave_ids=[1], function_codes=[5, 15], addresses=list(range(0, 10)))
    def write_data_store(slave_id, function_code, address, value):
        """" Set value for address. """
        data_store[address] = value

    if __name__ == '__main__':
        try:
            app.serve_forever()
        finally:
            app.shutdown()
            app.server_close()

Doing a Modbus request requires even less code:

..
    Because GitHub doesn't support the include directive the source of
    scripts/examples/simple_data_store.py has been copied to this file.

.. code:: python

    #!/usr/bin/env python
    # scripts/examples/simple_tcp_client.py
    from argparse import ArgumentParser
    from socket import create_connection

    from umodbus import conf
    from umodbus.client import tcp

    # Enable values to be signed (default is False).
    conf.SIGNED_VALUES = True

    # Parse command line arguments
    parser = ArgumentParser()
    parser.add_argument("-a", "--address", default="localhost:502")

    args = parser.parse_args()
    if ":" not in args.address:
        args.address += ":502"
    host, port = args.address.rsplit(":", 1)
    port = int(port)

    # Returns a message or Application Data Unit (ADU) specific for doing
    # Modbus TCP/IP.
    message = tcp.write_multiple_coils(slave_id=1, starting_address=1, values=[1, 0, 1, 1])

    with create_connection((host, port)) as sock:
        # Response depends on Modbus function code. This particular returns the
        # amount of coils written, in this case it is.
        response = tcp.send_message(message, sock)


Features
--------

The following functions have been implemented for Modbus TCP and Modbus RTU:

* 01: Read Coils
* 02: Read Discrete Inputs
* 03: Read Holding Registers
* 04: Read Input Registers
* 05: Write Single Coil
* 06: Write Single Register
* 15: Write Multiple Coils
* 16: Write Multiple Registers

Other featues:

* Support for signed and unsigned register values.

License
-------

uModbus software is licensed under `Mozilla Public License`_. © 2018 `Advanced
Climate Systems`_.

.. External References:
.. _Advanced Climate Systems: http://www.advancedclimate.nl/
.. _GitHub: https://github.com/AdvancedClimateSystems/uModbus/
.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
.. _Mozilla Public License: https://github.com/AdvancedClimateSystems/uModbus/blob/develop/LICENSE
.. _Read the Docs: http://umodbus.readthedocs.org/en/latest/
