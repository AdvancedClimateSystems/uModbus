Configuration
=============

:attr:`umodbus.conf` is a global configuration object and is an instance of
`umodbus.config.Config`. This instance can be used like this:

.. code:: python
    
  from umodbus import conf

  conf.SIGNED_VALUES = True 


.. module:: umodbus.config

.. autoclass:: Config
    :members:  SIGNED_VALUES

