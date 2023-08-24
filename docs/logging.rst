Logging
============

Within Clappform, it is possible to activate logging on various levels and view the system's operations. This feature is intended for potential debugging of complex systems implemented within the **Clappform** ecosystem, for example when used with the Worker.

Usage
------

.. code:: python

    >>> import logging
    >>> from clappform import Clappform
    >>> import clappform.dataclasses as r
    ...
    >>> logging.basicConfig()
    >>> logging.getLogger().setLevel(logging.DEBUG)
    ... 
    >>> requests_log = logging.getLogger("urllib3")
    >>> requests_log.setLevel(logging.DEBUG)
    >>> requests_log.propagate = True
    ... 
    >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
    ... DEBUG:urllib3.util.retry:Converted retries value: 3 -> Retry(total=3, connect=None, read=None, redirect=None, status=None)
    >>> apps = c.get_apps(r.App())
    ... DEBUG:urllib3.connectionpool:Starting new HTTPS connection (1): app.clappform.com:443
    ... DEBUG:urllib3.connectionpool:https://app.clappform.com:443 "POST /api/auth HTTP/1.1" 200 1912
    ... DEBUG:urllib3.connectionpool:https://app.clappform.com:443 "GET /api/apps?extended=false HTTP/1.1" 200 37106
    >>> for app in apps:
    >>>     print(app.name)
    ... App(collections=13, description='Default Clappform appl...
    ... App(collections=12, description='Secondary default Clap...