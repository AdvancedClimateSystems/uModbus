Decompose requests
------------------

A Modbus requests and responses contains a Application Data Unit (ADU) which
contains a Protocol Data Unit (PDU). The ADU is the enveloppe containing a
message, the PDU is the message itself. Modbus requests can be send
communication layers layers, like RTU or TCP/IP. The ADU for these layers
differs.  But the PDU, the message, has always the same strcuture, independent
of the way it's transported.

ADU for TCP/IP requests and responses
=====================================

.. note:: This documentation is based on `MODBUS Messaging on TCP/IP
    Implementation Guide V1.0b`_.

.. note:: When in this Wanneer we het over Modbus requests hebben in dit hoofdstuk, dan gaat
    het over Modbus TCP/IP requests.

Below you see an hexidecimal presentation of request over TCP/IP with Modbus
function code 1. It requests data of slave with 1, starting at coil 100, for
the length of 1 coil::

    >>> # Read coils, starting from coil 100 for the length of 1 coil.
    >>> adu = b'\x00\x08\x00\x00\x00\x06\x01\x01\x00d\x00\x01'

The length of the ADU is 12 bytes::

    >>> len(adu)
    12

Besides a PDU, an ADU for requests and responses also contains Modbus
Application Protocol header (MBAP header). This header is what makes modbus
TCP/IP requests and responsen different from their counterparts send over a
serial line using RTU. This header is 7 bytes long::

    >>> mbap = adu[:7]
    >>> mbap
    b'\x00\x08\x00\x00\x00\x06\x01'

The MBAP header contains the following fields:

+------------------------+--------------------+--------------------------------------+
| **Field**              | **Length** (bytes) | **Description**                      | 
+------------------------+--------------------+--------------------------------------+
| Transaction identifier | 2                  | Identification of a                  | 
|                        |                    | Modbus request/response transaction. | 
+------------------------+--------------------+--------------------------------------+
| Protocol identifier    | 2                  | Protocol ID, is 0 for Modbus.        | 
+------------------------+--------------------+--------------------------------------+
| Length                 | 2                  | Number of following bytes            | 
+------------------------+--------------------+--------------------------------------+
| Unit identifier        | 1                  | Identification of a                  | 
|                        |                    | remote slave                         | 
+------------------------+--------------------+--------------------------------------+

When unpacked, these fields have the following values::

    >>> transaction_id = mbap[:2]
    >>> transaction_id
    b'\x00\x08'
    >>> protocol_id = mbap[2:4]
    >>> protocol_id
    b'\x00\x00'
    >>> length = mbap[4:6]
    >>> length
    b'\x00\x06'
    >>> unit_id = mbap[6:]
    >>> unit_id
    b'\0x01'

The request in words: a request with Transaction ID 8 for unit/slave 1. The
request uses Protocol ID 0, which is the Modbus protocol. The length of the
bytes after the Length field is 6 bytes. These 6 bytes are Unit Identifier (1
byte) + PDU (5 bytes).


.. _MODBUS Messaging on TCP/IP Implementation Guide V1.0b: http://modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf
