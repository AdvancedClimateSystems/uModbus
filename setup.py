#!/usr/bin/env python
from setuptools import setup

setup(name='uModbus',
      version='0.1.0',
      author='Auke Willem Oosterhoff',
      author_email='oosterhoff@baopt.nl',
      description='Implementation of the Modbus protocol in pure Python.',
      url='https://github.com/AdvancedClimateSystems/umodbus/',
      packages=[
          'umodbus',
      ],
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Embedded Systems',
      ])
