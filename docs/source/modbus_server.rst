Modbus Server
-------------

Viewpoint
=========

The uModbus server code is built with routing in mind. Routing (groups of)
requests to a certain callback is easy. This is in contrast with with
other Modbus implementation which often focus on reading and writing from a
data store.

Because of this difference in viewpoint uModbus doesn't know the concept of
Modbus' data models like discrete inputs, coils, input registers, holding
registers and their read/write properties.

Routing
=======

The routing system was inspired by Flask_. Like Flask, uModbus requires a global
app or server. This server contains a route map. Routes can be added to the
route map.

The following code example demonstrates how to implement a very simple data
store for 10 addresses.

Modbus TCP example
==================

.. include:: ../../scripts/examples/simple_tcp_server.py
    :code: python

Modbus RTU example
==================

.. include:: ../../scripts/examples/simple_rtu_server.py
    :code: python

.. _Flask: http://flask.pocoo.org/
