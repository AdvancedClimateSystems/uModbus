Decompose requests
------------------

A Modbus requests and responses contains a Application Data Unit (ADU) which
contains a Protocol Data Unit (PDU). The ADU is the enveloppe containing a
message, the PDU is the message itself. Modbus requests can be send
communication layers layers, like RTU or TCP/IP. The ADU for these layers
differs.  But the PDU, the message, has always the same strcuture, independent
of the way it's transported.

PDU
===

.. automodule:: umodbus.client.pdu

ADU for TCP/IP requests and responses
=====================================

.. automodule:: umodbus.client.tcp


.. _MODBUS Messaging on TCP/IP Implementation Guide V1.0b: http://modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf
.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
