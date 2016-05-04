Modbus TCP
----------

Example
=======

All functions codes for Modbus TCP/IP are supported. U can use the client like
this:

.. include:: ../../../scripts/examples/simple_tcp_client.py
    :code: python


API
===

.. autofunction:: umodbus.client.tcp.send_message

.. autofunction:: umodbus.client.tcp.parse_response_adu

.. autofunction:: umodbus.client.tcp.read_coils

.. autofunction:: umodbus.client.tcp.read_discrete_inputs

.. autofunction:: umodbus.client.tcp.read_holding_registers

.. autofunction:: umodbus.client.tcp.read_input_registers

.. autofunction:: umodbus.client.tcp.write_single_coil

.. autofunction:: umodbus.client.tcp.write_single_register

.. autofunction:: umodbus.client.tcp.write_multiple_coils

.. autofunction:: umodbus.client.tcp.write_multiple_registers
