.. clappform documentation master file, created by
   sphinx-quickstart on Fri Nov 11 10:53:58 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Clappform's API Wrapper
==================================
**Clappform** allows one to easily connect and interact with a Clappform B.V. API. There is no need to manually program HTTP requests to authenticate and consume the API. Many resources of the API are able to be created, read, updated and deleted. To start using **Clappform** with logging::

    >>> import logging
    >>> from clappform import Clappform
    >>> import clappform.dataclasses as r
    >>> logging.basicConfig()
    >>> logging.getLogger().setLevel(logging.DEBUG)
    >>> requests_log = logging.getLogger("urllib3")
    >>> requests_log.setLevel(logging.DEBUG)
    >>> requests_log.propagate = True
    >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
    DEBUG:urllib3.util.retry:Converted retries value: 3 -> Retry(total=3, connect=None, read=None, redirect=None, status=None)
    >>> apps = c.get_apps(r.App())
    DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): app.clappform.com:443
    DEBUG:urllib3.connectionpool:https://app.clappform.com:443 "POST /api/auth HTTP/1.1" 200 1912
    DEBUG:urllib3.connectionpool:https://app.clappform.com:443 "GET /api/apps?extended=false HTTP/1.1" 200 37106
    >>> for app in apps:
    ...     print(app.name)


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Developer interface
===================

.. automodule:: clappform
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: clappform.dataclasses
   :members:
   :undoc-members:
   :show-inheritance:

.. automodule:: clappform.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
