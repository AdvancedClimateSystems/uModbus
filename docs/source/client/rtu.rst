Modbus RTU
----------

Example
=======

.. note::
    uModbus doesn't support all functions defined for Modbus RTU. It currently
    support the following functions:

    * 01: Read Coils
    * 02: Read Discrete Inputs
    * 03: Read Holding Registers
    * 04: Read Input Registers
    * 05: Write Single Coil
    * 06: Write Single Register
    * 15: Write Multiple Coils
    * 16: Write Multiple Registers

.. include:: ../../../scripts/examples/simple_rtu_client.py
    :code: python

API
===

.. autofunction:: umodbus.client.serial.rtu.send_message

.. autofunction:: umodbus.client.serial.rtu.parse_response_adu

.. autofunction:: umodbus.client.serial.rtu.read_coils

.. autofunction:: umodbus.client.serial.rtu.read_discrete_inputs

.. autofunction:: umodbus.client.serial.rtu.read_holding_registers

.. autofunction:: umodbus.client.serial.rtu.read_input_registers

.. autofunction:: umodbus.client.serial.rtu.write_single_coil

.. autofunction:: umodbus.client.serial.rtu.write_single_register

.. autofunction:: umodbus.client.serial.rtu.write_multiple_coils

.. autofunction:: umodbus.client.serial.rtu.write_multiple_registers
