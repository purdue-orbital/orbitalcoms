***************
User Facing API
***************

.. currentmodule:: orbitalcoms


Station Factories
=================

.. autofunction:: create_socket_launch_station
.. autofunction:: create_socket_ground_station
.. autofunction:: create_serial_launch_station
.. autofunction:: create_serial_ground_station


Launch Station
==============

.. autoclass:: LaunchStation
   :special-members: __init__
   :inherited-members:
   :undoc-members:
   :members:


Ground Station
==============

.. autoclass:: GroundStation
   :special-members: __init__
   :private-members: _is_valid_state_change
   :inherited-members:
   :undoc-members:
   :members:


Messages
========

.. autofunction:: construct_message

.. autoclass:: ComsMessage
   :inherited-members:
   :undoc-members:
   :members: