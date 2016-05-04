Changelog
=========

0.6.0 (Not released yet)
++++++++++++++++++++++++

**Feature**

* `#24`  Add Modbus RTU client.

.. _#24: https://github.com/AdvancedClimateSystems/uModbus/issues/24

0.5.0 (2016-05-03)
++++++++++++++++++

**Bugs**

* `#36`_ Parameter `function_code` is missing in signature of routes.

.. _#36: https://github.com/AdvancedClimateSystems/uModbus/issues/36

0.4.2 (2016-04-07)
++++++++++++++++++

**Bugs**

* `#20`_ uModbus should close connection when client closes it.

.. _#20: https://github.com/AdvancedClimateSystems/uModbus/issues/20

0.4.1 (2016-01-22)
++++++++++++++++++

**Bugs**

* `#31`_  Add subpackages `umodbus.client` and `umodbus._functions` to `setup.py`.

.. _#31: https://github.com/AdvancedClimateSystems/uModbus/issues/31

0.4.0 (2016-01-22)
++++++++++++++++++

**Features**

* `#23`_  Implemenent Modbus client.
* `#28`_  Implemenent signed integers for Modbus client.

.. _#23: https://github.com/AdvancedClimateSystems/uModbus/issues/23
.. _#28: https://github.com/AdvancedClimateSystems/uModbus/issues/28

0.3.1 (2015-12-12)
++++++++++++++++++

**Bugs**

* `#18`_ Edit interface of `get_server` so socket options can now be set
  easily.

.. _#18: https://github.com/AdvancedClimateSystems/uModbus/issues/18

0.3.0 (2015-12-05)
++++++++++++++++++

**Features**

* `#17`_ `RequestHandler.handle()` can be overridden easily.

.. _#17: https://github.com/AdvancedClimateSystems/uModbus/issues/17

0.2.0 (2015-11-19)
++++++++++++++++++

**Features**

* `#10`_ Support for signed values.

**Bugs**

* `#13`_ Fix shutdown of server in `simple_data_store.py`

.. _#10: https://github.com/AdvancedClimateSystems/uModbus/issues/10
.. _#13: https://github.com/AdvancedClimateSystems/uModbus/issues/13

0.1.2 (2015-11-16)
++++++++++++++++++

**Bugs**

* `#8`_ `WriteMultipleCoils.create_from_request_pdu` sometimes doesn't unpack PDU correct.

.. _#8: https://github.com/AdvancedClimateSystems/uModbus/issues/8

0.1.1 (2015-11-12)
++++++++++++++++++

**Bugs**

* `#7`_ Fix default stream and log level of `utils.log_to_stream`.

.. _#7: https://github.com/AdvancedClimateSystems/uModbus/issues/7

0.1.0 (2015-11-10)
++++++++++++++++++

* First release.
