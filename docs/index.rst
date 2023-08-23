Welcome to Clappform's API Wrapper
==================================
**Clappform** allows one to easily connect and interact with a Clappform B.V. API. There is no need to manually program HTTP requests to authenticate and consume the API. Many resources of the API are able to be created, read, updated and deleted. To start using **Clappform** with logging::

Quick start
------------

.. code:: python

   from clappform import Clappform
   import clappform.dataclasses as c_dataclasses

   # Get a environment token from the given environment
   c_auth = Clappform("ENVIRONMENT_URL", "J.Doe@clappform.com", "SUPERSECRETPASSWORD")

   # Get all applications
   apps = c_auth.Get(c_dataclasses.App())

   for app in apps:
      print(app.name)


Usage
------
Check out the :doc:`usage` section for further information.


Contents
--------

.. toctree::

   usage




.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

.. Developer interface
.. ===================

.. .. automodule:: clappform
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. .. automodule:: clappform.dataclasses
..    :members:
..    :undoc-members:
..    :show-inheritance:

.. .. automodule:: clappform.exceptions
..    :members:
..    :undoc-members:
..    :show-inheritance:
