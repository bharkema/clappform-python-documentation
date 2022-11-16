# Clappform
**Clappform** is a wrapper for a Clappform B.V. API written in Python.

```python
>>> from clappform import Clappform
>>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
>>> apps = c.get_apps()
>>> for app in apps:
...     print(app.name)
'Clappform'
'Default'
```

Clappform allows you to interact with the Clappform API for a given domain. For many of the resources that the Clappform API provides the simple ``get``, ``create``, ``update`` and ``delete`` methods can be used. Authentication is done transparently, so there is no need to manually authenticate.

## Developer interface is available on [Read The Docs](https://clappform.com)
