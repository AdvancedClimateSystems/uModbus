.. image:: https://travis-ci.org/AdvancedClimateSystems/uModbus.svg
    :target: https://travis-ci.org/AdvancedClimateSystems/uModbus

.. image:: https://coveralls.io/repos/AdvancedClimateSystems/uModbus/badge.svg?service=github
  :target: https://coveralls.io/github/AdvancedClimateSystems/uModbus


uModbus
=======
uModbus or (μModbus) is a pure Python implementation of the Modbus protcol as
described in the `MODBUS Application Protocol Specification V1.1b3`_. The "u"
or "μ" in the name comes from the the SI prefix "micro-". uModbus is very small
and lightweight. uModbus is open source and licenced under `Mozilla Public
License`_. The source can be found on GitHub_.

Routing Modbus requests is easy:

.. code:: python

    from umodbus import get_server

    server = get_server('localhost', 502)

    @server.route(slave_ids=[1], function_codes=[3, 4], addresses=list(range(100, 200)))
    def return_address(slave_id, address):
        """ Return address. """
        print('Called with slave_id {0} and address {1}.'.format(slave_id, address))
        return address

    try:
        server.serve_forever()
    finally:
        server.shutdown()

.. External References:
.. _GitHub: https://github.com/AdvancedClimateSystems/uModbus/
.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
.. _Mozilla Public License: https://github.com/AdvancedClimateSystems/uModbus/blob/develop/LICENSE
