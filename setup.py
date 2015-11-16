#!/usr/bin/env python
"""
uModbus is a pure Python implementation of the Modbus protocol with support
for Python 2.7, 3.3, 3.4, 3.5 and Pypy. uModbus has no runtime depedencies.

"""
from setuptools import setup

setup(name='uModbus',
      version='0.1.2',
      author='Auke Willem Oosterhoff',
      author_email='oosterhoff@baopt.nl',
      description='Implementation of the Modbus protocol in pure Python.',
      url='https://github.com/AdvancedClimateSystems/umodbus/',
      long_description=__doc__,
      license='MPL',
      packages=[
          'umodbus',
      ],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Embedded Systems',
      ])
