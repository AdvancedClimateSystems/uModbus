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

.. note:: This section is based on `MODBUS Messaging on TCP/IP
    Implementation Guide V1.0b`_.

.. note:: When in this Wanneer we het over Modbus requests hebben in dit hoofdstuk, dan gaat
    het over Modbus TCP/IP requests.

Below you see an hexidecimal presentation of request over TCP/IP with Modbus
function code 1. It requests data of slave with 1, starting at coil 100, for
the length of 3 coils::

    >>> # Read coils, starting from coil 100 for the length of 3 coils.
    >>> adu = b'\x00\x08\x00\x00\x00\x06\x01\x01\x00d\x00\x03'

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

PDU

.. note:: This section is based on `MODBUS Application Protocol Specification
    V1.1b3`_

The PDU is the message and is indepedent of the underlying communication
layers. The PDU for Modbus requests contains a function code and request data.
The response contains a function code or exception code with response data.

The size of the PDU varies, depending on response. Below you see the request
PDU with function code 1, requesting status of 3 coils, starting from coil 100.

    >>> req_pdu = b'\x01\x00d\x00\x03'
    >>> function_code = req_pdu[:1]
    >>> function_code
    b'\x01'
    >>> starting_address = req_pdu[1:3]
    >>> starting_address
    b'\x00d'
    >>> quantity = req_pdu[3:]
    >>> quantity
    b'\x00\x03'

A response PDU could look like this::

    >>> resp_pdu = b'\x01\x01\x06'
    >>> function_code = resp_pdu[:1]
    >>> function_code
    b'\x01'
    >>> byte_count = resp[1:2]
    >>> byte_count
    b'\x01'
    >>> coil_status = resp[2:]
    'b\x06'

This response PDU contains function code 1 and the status of the 3 coils is
described using 1 byte. The binary status of coils 102, 101 en 100 sum up to 6.
Decimal 6 is binary 110::

    >>> bin(coil_status)
    '0b110'

The least significant bit of the coil status contains the status of the coil
addressed in the request. So according to this response PDU the status of the
coils is as follows:

+----------+------------+
| **Coil** | **Status** |
+----------+------------+
| 100      | 0          |
+----------+------------+
| 101      | 1          |
+----------+------------+
| 102      | 1          |
+----------+------------+


.. _MODBUS Messaging on TCP/IP Implementation Guide V1.0b: http://modbus.org/docs/Modbus_Messaging_Implementation_Guide_V1_0b.pdf
.. _MODBUS Application Protocol Specification V1.1b3: http://modbus.org/docs/Modbus_Application_Protocol_V1_1b3.pdf
