Changelog
=========

1.0.4 (2020-08-27)
++++++++++++++++++

**Bugs**

* `#90`_ Fix error code of 2 Modbus errors. Thanks `@rgov`!
* `#100`_ Improve check for missing routes. Thanks `@rgov`!
* `#101`_ Fix crash if 1 of arguments of `umodbus.server.route` is `None` .Thanks `@rgov`!
* `#105`_ Fix byte count when for WriteMultipleCoils. Thank `@acolomb`!

**Improvements**

* `#102`_ Remove redundant exception traceback. Thanks `@rgov`!
* `#103`_ Fix error code of 2 Modbus errors. Thanks `@rgov`!
* `#104`_ Denote hex dump of ADU in debug log. Thanks `@rgov`!

.. _#90: https://github.com/AdvancedClimateSystems/uModbus/issues/90
.. _#100: https://github.com/AdvancedClimateSystems/uModbus/issues/100
.. _#101: https://github.com/AdvancedClimateSystems/uModbus/issues/101
.. _#102: https://github.com/AdvancedClimateSystems/uModbus/issues/102
.. _#103: https://github.com/AdvancedClimateSystems/uModbus/issues/103
.. _#104: https://github.com/AdvancedClimateSystems/uModbus/issues/103
.. _#105: https://github.com/AdvancedClimateSystems/uModbus/issues/105

1.0.3 (2019-12-04)
++++++++++++++++++

* `#76`_ Remove use of deprecated `inspect.getargspec()` for Python>=3.5.
* Drop support for Python 3.3
* Add support for Python 3.7 and Python 3.8

.. _#76: https://github.com/AdvancedClimateSystems/uModbus/issues/76

1.0.2 (2018-05-22)
++++++++++++++++++

I released uModbus 1.0.1 without updating the version number in `setup.py`.
This releases fixes this.

1.0.1 (2018-05-22)
++++++++++++++++++

`@wthomson`_ has fixed a couple of typo's in the documentation. Thanks!

**Bugs**

* `#49`_ Fix clients being to greedy when reading response. Thanks `@lutostag`_!

.. _#49: https://github.com/AdvancedClimateSystems/uModbus/issues/49
.. _@lutostag: https://github.com/lutostag
.. _@wthomson: https://github.com/wthomson

1.0.0 (2018-01-06)
++++++++++++++++++

**Bugs**

* `#50`_ Fix handling of empty ADU's.

.. _#50: https://github.com/AdvancedClimateSystems/uModbus/issues/50

0.8.2 (2016-11-11)
++++++++++++++++++

**Bugs**

* `#47`_ Fix import errors in sample code. Thanks `@tiagocoutinho`_!

.. _#47: https://github.com/AdvancedClimateSystems/uModbus/issues/47
.. _@tiagocoutinho: https://github.com/tiagocoutinho

0.8.1 (2016-11-02)
++++++++++++++++++

**Bugs**

* `#27`_ Route is called with wrong value when one write single coil with value 1.
* `#42`_ Drop support for PyPy.

.. _#27: https://github.com/AdvancedClimateSystems/uModbus/issues/27
.. _#42: https://github.com/AdvancedClimateSystems/uModbus/issues/42

0.8.0 (2016-10-31)
++++++++++++++++++

**Features**

* `#48`_ Update to pyserial 3.2.1

.. _#48: https://github.com/AdvancedClimateSystems/uModbus/issues/48

0.7.2 (2016-09-27)
++++++++++++++++++

**Bugs**

* `#44`_ Remove print statement.
* `#46`_ Transaction ID overflow. Thanks `@greg0pearce`_

.. _#44: https://github.com/AdvancedClimateSystems/uModbus/issues/44
.. _#46: https://github.com/AdvancedClimateSystems/uModbus/issues/46
.. _@greg0pearce`: https://github.com/greg0pearce

0.7.1 (01-09-2016)
++++++++++++++++++

**Bugs**

* `#41`_ RTU server doesn't handle frames correct.

.. _#41: https://github.com/AdvancedClimateSystems/uModbus/issues/41

0.7.0 (29-07-2016)
++++++++++++++++++

**Features**

* `#22`_ Add Modbus RTU server.

**Bugs**

* `#39`_  Merge functions module with _functions package.
* `#37`_  Pretty print binary data in shell.
* `#38`_  Fix type in sumple_rtu_client.py

.. _#22: https://github.com/AdvancedClimateSystems/uModbus/issues/22
.. _#29: https://github.com/AdvancedClimateSystems/uModbus/issues/29
.. _#37: https://github.com/AdvancedClimateSystems/uModbus/issues/37
.. _#38: https://github.com/AdvancedClimateSystems/uModbus/issues/38


0.6.0 (2016-05-08)
++++++++++++++++++

**Features**

* `#24`_  Add Modbus RTU client.

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
