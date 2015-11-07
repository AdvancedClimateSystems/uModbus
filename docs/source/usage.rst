Usage
-----

Viewpoint
=========

uModbus is build with routing in mind. Routing (groups of) requests to a
certain callback must be easy. This is in contrast with with other Modbus
implementation which often focus on reading and writing from a data store.

Because of this difference in view point uModbus doesn't know the concepts of
Modbus' data models (discrete inputs, coils, input registers and holding
registers) and their read/write properties.

Routing
-------

The route system was inspired by Flask_. Like Flask, uModbus requires a global
app or server. This server contains a route map. Routes can be added to this
route map. The following example demostrates how to route all Modbus requests
for slave 1, function code 1 en 2 addressed to address 0 to the endpoint
`read_gpio_status`.

.. code:: python

    from umodbus import get_server
    from collections import defaultdict

    # A very simple data store which maps addresss against their values.
    data_store = dict(int)

    server = get_server('localhost', 502)

    @server.route(slave_ids=[1], functions_codes=[3, 4], addresses=list(range(0, 10)))
    def read_data_store(slave_id, address):
        """" Return value of address. """
        return data_store[address]

    @server.route(slave_ids=[1], functions_codes=[3, 4], addresses=list(range(0, 10)))
    def write_data_store(slave_id, address, value):
        """" Set value for address. """
        data_store[address] = value

    try:
        server.serve_forever()
    finally:
        server.stop()


.. External references
.. _Flask: http://flask.pocoo.org/
