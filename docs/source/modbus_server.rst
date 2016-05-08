Modbus Server
-------------

Viewpoint
=========

The uModbus server code is build with routing in mind. Routing (groups of)
requests to a certain callback must be easy. This is in contrast with with
other Modbus implementation which often focus on reading and writing from a
data store.

Because of this difference in view point uModbus doesn't know the concepts of
Modbus' data models like discrete inputs, coils, input registers and holding
registers and their read/write properties.

Routing
=======

The route system was inspired by Flask_. Like Flask, uModbus requires a global
app or server. This server contains a route map. Routes can be added to this
route map.

The following code example demonstrates how to implement a very simple data
store for 10 addresses.

Sample use
==========

.. include:: ../../scripts/examples/simple_data_store.py
    :code: python

.. _Flask: http://flask.pocoo.org/
