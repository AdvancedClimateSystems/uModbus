Decompose requests
------------------

Modbus requests and responses contain an Application Data Unit (ADU) which
contains a Protocol Data Unit (PDU). The ADU is an envelope containing a
message, the PDU is the message itself. Modbus requests can be sent via
two communication layers, RTU or TCP/IP. The ADU for these layers
differs.  But the PDU, the message, always has the same strcuture, regardless
of the way it's transported.

PDU
===

.. automodule:: umodbus.functions

ADU for TCP/IP requests and responses
=====================================

.. automodule:: umodbus.client.tcp


.. _MODBUS Messaging on TCP/IP Implementation Guide V1.0b: http://modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf
.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf

ADU for RTU requests and responses
==================================

.. automodule:: umodbus.client.serial.rtu

.. _MODBUS over Serial Line Specification and Implementation Guide V1.02: http://www.modbus.org/docs/Modbus_over_serial_line_V1_02.pdf
