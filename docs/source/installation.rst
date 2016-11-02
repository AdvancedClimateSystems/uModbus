Installation
------------

uModbus has been tested_ on Python 2.7 and Python 3.3+.

As package
==========

uModbus is available on Pypi_ and can be installed through Pip_::

    $ pip install umodbus

Or you can install from source_ using `setup.py`::

    $ python setup.py install


For development, debugging and testing
======================================

uModbus has no runtime dependencies. However to run the the tests or build the
documentation some dependencies are required. They are listed in
dev_requirements.txt_ and can be installed through Pip::

    $ pip install -r dev_requirements.txt

Now you can build the docs::

    $ sphinx-build -b html docs/source docs/build

Or run the tests::

    $ py.test tests


.. External references:
.. _dev_requirements.txt: https://github.com/AdvancedClimateSystems/uModbus/blob/develop/dev_requirements.txt
.. _Pypi: https://pypi.python.org/pypi/uModbus
.. _Pip: https://pip.readthedocs.org/en/stable/
.. _source: https://github.com/AdvancedClimateSystems/umodbus
.. _tested: https://travis-ci.org/AdvancedClimateSystems/uModbus
