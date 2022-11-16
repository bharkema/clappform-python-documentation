"""
Clappform API Wrapper
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2022 Clappform B.V..
:license: MIT, see LICENSE for more details.
"""
__requires__ = ["requests==2.28.1", "Cerberus==1.3.4"]
# Python Standard Library modules
from dataclasses import asdict
import math
import time

# PyPi modules
from cerberus import Validator
import requests as r

# clappform Package imports.
from . import dataclasses as dc
from .exceptions import HTTPError

# Metadata
__version__ = "1.0.0"
__author__ = "Clappform B.V."
__email__ = "info@clappform.com"
__license__ = "MIT"
__doc__ = "Clappform Python API wrapper"


class Clappform:
    """:class:`Clappform <Clappform>` class is used to more easily interact with an Clappform
    environement through the API.

    :param str base_url: Base URL of a Clappform environment e.g. ``https://app.clappform.com``.
    :param str username: Username used in the authentication :meth:`auth <auth>`.
    :param str password: Password used in the authentication :meth:`auth <auth>`.

    Most routes of the Clappform API require authentication. For the routes in the Clappform API
    that require authentication :class:`Clappform <Clappform>` will do the authentication for you.

    In the example below ``c.get_apps()`` uses a route which requires authentication.
    :class:`Clappform <Clappform>` does the authentication for you.

    Usage::

        >>> from clappform import Clappform
        >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
        >>> apps = c.get_apps()
        >>> for app in apps:
        ...     print(app.name)
    """

    _auth = None

    def __init__(self, base_url: str, username: str, password: str):
        self._base_url: str = f"{base_url}/api"

        #: Username to use in the :meth:`auth <auth>`
        self.username: str = username

        #: Password to use in the :meth:`auth <auth>`
        self.password: str = password

    def _default_user_agent(self) -> str:
        """Return a string with version of requests and clappform packages."""
        requests_ua = r.utils.default_user_agent()
        return f"clappform/{__version__} {requests_ua}"

    def _request(self, method: str, path: str, timeout=10, **kwargs):
        """Implements :class:`requests.request`."""
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self._default_user_agent()
        resp = r.request(
            method,
            f"{self._base_url}{path}",
            headers=headers,
            timeout=timeout,
            **kwargs,
        )
        doc = resp.json()

        e_occurance = None  # Exception occured if its not None after try block.
        try:
            resp.raise_for_status()
        except r.exceptions.HTTPError as e:
            e_occurance = e
        if e_occurance is not None:
            raise HTTPError(
                doc["message"],
                code=doc["code"],
                response_id=doc["response_id"],
                response=resp,
            )
        return doc

    def _private_request(self, method: str, path: str, **kwargs):
        """Implements :meth:`_request` and adds Authorization header."""
        if not isinstance(self._auth, dc.Auth):
            self.auth()
        if not self._auth.is_token_valid():
            self.auth()

        headers = kwargs.pop("headers", {})
        headers["Authorization"] = f"Bearer {self._auth.access_token}"
        return self._request(method, path, headers=headers, **kwargs)

    def auth(self) -> None:
        """Sends an authentication request. Gets called whenever authentication is required.

        The :attr:`_auth` attribute is set to a newly constructed
        :class:`clappform.dataclasses.Auth` object.
        """
        document = self._request(
            "POST",
            "/auth",
            json={"username": self.username, "password": self.password},
        )
        self._auth = dc.Auth(**document["data"])

    def verify_auth(self) -> dc.ApiResponse:
        """Verify against the API if the authentication is valid.

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        document = self._private_request("POST", "/auth/verify")
        return dc.ApiResponse(**document)

    def version(self) -> dc.Version:
        """Get the current version of the API.

        :returns: Version Object
        :rtype: clappform.dataclasses.Version
        """
        document = self._private_request("GET", "/version")
        return dc.Version(**document["data"])

    def _app_path(self, app) -> str:
        if isinstance(app, dc.App):
            return app.path()
        if isinstance(app, str):
            return dc.App._path.format(app)
        raise TypeError("app arg is not of type {dc.App} or {str}, got {type(app)}")

    def get_apps(self) -> list[dc.App]:
        """Gets all apps.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> apps = c.get_apps()

        :returns: List of :class:`clappform.dataclasses.App` or empty list if there are no apps.
        :rtype: list[clappform.dataclasses.App]
        """
        document = self._private_request("GET", "/apps")
        return [dc.App(**obj) for obj in document["data"]]

    def get_app(self, app) -> dc.App:
        """Get a single app.

        :param app: App to get from the API
        :type app: :class:`str` | :class:`clappform.dataclasses.App`

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> app = c.get_app("clappform")
            >>> app = c.get_app(app)

        :returns: App Object
        :rtype: clappform.dataclasses.App
        """
        path = self._app_path(app)
        document = self._private_request("GET", path)
        return dc.App(**document["data"])

    def create_app(self, app_id: str, name: str, desc: str, settings: dict) -> dc.App:
        """Create a new app.

        :param str app_id: String for internal identification.
        :param str name: Display name for the new app.
        :param str desc: Description for the new app.
        :param dict settings: Configuration options for an app.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> new_app = c.create_app("foo", "Foo", "Foo Bar", {})

        :returns: Newly created app
        :rtype: clappform.dataclasses.App
        """
        document = self._private_request(
            "POST",
            "/app",
            json={
                "id": app_id,
                "name": name,
                "description": desc,
                "settings": settings,
            },
        )
        return dc.App(**document["data"])

    def update_app(self, app) -> dc.App:
        """Update an existing app.

        :param app: Modified app object.
        :type app: clappform.dataclasses.App

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> app = c.get_app("foo")
            >>> app.name = "Bar"
            >>> app = c.update_app(app)

        :returns: Updated app object
        :rtype: clappform.dataclasses.App
        """
        if not isinstance(app, dc.App):
            raise TypeError("app arg is not of type {dc.App}, got {type(app)}")
        document = self._private_request("PUT", app.path(), json=asdict(app))
        return dc.App(**document["data"])

    def delete_app(self, app) -> dc.ApiResponse:
        """Delete an app.

        :param app: App to delete from the API
        :type app: :class:`str` | :class:`clappform.dataclasses.App`

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> c.delete_app("foo")

        :returns: Response from the API
        :rtype: clappform.dataclasses.ApiResponse
        """
        path = self._app_path(app)
        document = self._private_request("DELETE", path)
        return dc.ApiResponse(**document)

    def _collection_path(self, app, collection):
        if isinstance(collection, dc.Collection):
            return collection.path()
        if not isinstance(collection, str):
            raise TypeError(
                "collection arg is not of type {dc.Collection} or {str}, got {type(collection)}"
            )
        app = self._app_path(app).replace("/app/", "")
        return dc.Collection._path.format(app, collection)

    def get_collections(self, app=None, extended=0) -> list[dc.Collection]:
        """Get all the collections.

        The `extended` parameter allows an integer value from 0 - 3.

        :param app: Optional return only collections from specified app, default: ``None``.
        :type app: clappform.dataclasses.Collection
        :param extended: Optional level of detail for each collection, default: ``0``.
        :type extended: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> app = c.get_app("foo")
            >>> collections = c.get_collections(extended=3)
            >>> collections = c.get_collections(app=app)

        :raises ValueError: extended value not in [0, 1, 2 ,3]

        :returns: List of Collections or empty list if there are no collections
        :rtype: list[clappform.dataclasses.Collection]
        """
        document = self._private_request("GET", f"/collections?extended={extended}")
        if isinstance(app, dc.App):
            return [
                dc.Collection(**obj)
                for obj in list(filter(lambda x: x["app"] == app.id, document["data"]))
            ]
        return [dc.Collection(**obj) for obj in document["data"]]

    def get_collection(
        self, collection, app=None, extended: int = 0, offset: int = 0
    ) -> dc.Collection:
        """Get a single collection.

        The `extended` parameter allows an integer value from 0 - 3.

        :param collection: Identifier for collection to retreive.
        :type collection: :class:`str` | :class:`clappform.dataclasses.Collection`
        :param app: Required when collection is of type :class:`str`, default: ``None``.
        :type app: :class:`str` | :class:`clappform.dataclasses.App`
        :param extended: Optional level of detail for each collection, default: ``0``.
        :type extended: int
        :param offset: Offset from which to retreive items, only useful when extended is ``3``.
        :type offset: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> app = c.get_app("foo")
            >>> collection = c.get_collection("bar", app=app)
            >>> collection = c.get_collection("bar", app="foo")
            >>> collection = c.get_collection(collection)

        The :class:`TypeError` is only raised when ``collection`` parameter is of type :class:`str`
        and ``app`` parameter is ``None``.

        :raises ValueError: extended value not in [0, 1, 2 ,3]
        :raises TypeError: app kwargs must be of type :class:`clappform.dataclasses.App` or
            :class:`str`.

        :returns: Collection Object
        :rtype: clappform.dataclasses.Collection
        """
        extended_range = range(4)  # API allows for 4 levels of extension.
        if extended not in extended_range:
            raise ValueError(f"extended {extended} not in {list(extended_range)}")
        if isinstance(collection, str) and app is None:
            raise TypeError(
                f"app kwarg cannot be {type(app)} when collection arg is {type(collection)}"
            )
        path = self._collection_path(app, collection)
        document = self._private_request(
            "GET", f"{path}?extended={extended}&offset={offset}"
        )
        return dc.Collection(**document["data"])

    def create_collection(self, app, slug: str, name: str, desc: str) -> dc.Collection:
        """Create a new Collection.

        :param app: App identifier to create collection for.
        :type app: :class:`str` | :class:`clappform.dataclasses.App`.
        :param str slug: Name used for internal identification.
        :param str name: Name of the collection.
        :param str desc: Description of what data the collection holds.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> app = c.get_app("foo")
            >>> new_collection = c.create_collection(app, "bar", "Bar", "Bar Collection")

        :returns: New Collection Object
        :rtype: clappform.dataclasses.Collection
        """
        path = self._app_path(app)
        path = path.replace("/app/", "/collection/")
        document = self._private_request(
            "POST",
            path,
            json={
                "slug": slug,
                "name": name,
                "description": desc,
            },
        )
        return dc.Collection(**document["data"])

    def update_collection(self, collection: dc.Collection) -> dc.Collection:
        """Update an existing collection.

        :param collection: Collection object to update
        :type collection: clappform.dataclasses.Collection

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> collection = c.get_collection("bar", app="foo")
            >>> collection.Name = "Spam & Eggs Collection"
            >>> collection = c.update_collection(collection)

        :riased TypeError: collection arg is not of type :class:`clappform.dataclasses.Collection`

        :returns: Updated Collection object
        :rtype: clappform.dataclasses.Collection
        """
        if not isinstance(collection, dc.Collection):
            raise TypeError(
                "collection arg is not of type {dc.Collection}, got {type(collection)}"
            )
        document = self._private_request(
            "PUT", collection.path(), json=asdict(collection)
        )
        return dc.Collection(**document["data"])

    def delete_collection(self, collection: dc.Collection) -> dc.ApiResponse:
        """Delete a collection.

        :param collection: Collection to remove
        :type collection: clappform.dataclasses.Collection

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> collection = c.get_collection("bar", app="foo")
            >>> c.delete_collection(collection)

        :returns: API reponse object
        :rtype: clappform.dataclasses.Collection
        """
        document = self._private_request("DELETE", collection.path())
        return dc.ApiResponse(**document)

    def _query_path(self, query) -> str:
        if isinstance(query, dc.Query):
            return query.path()
        if isinstance(query, str):
            return dc.Query._path.format(query)
        raise TypeError(
            "query arg is not of type {dc.Query} or {str}, got {type(query)}"
        )

    def get_queries(self) -> list[dc.Query]:
        """Get all queries.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> queries = c.get_queries()

        :returns: List of Query objects
        :rtype: list[clappform.dataclasses.Query]
        """
        document = self._private_request("GET", "/queries")
        if "data" not in document:
            return []
        return [dc.Query(**obj) for obj in document["data"]]

    def get_query(self, query) -> dc.Query:
        """Get single query.

        :param query: Query identifier
        :type query: :class:`str` | :class:`clappform.dataclasses.Query`

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> query = c.get_query("foo")

        :returns: Query object
        :rtype: clappfrom.dataclasses.Query
        """
        path = self._query_path(query)
        document = self._private_request("GET", path)
        return dc.Query(**document["data"])

    def source_query(self, query: dc.Query) -> dc.ApiResponse:
        """Source a query

        :param query: Query to source.
        :type query: clappform.dataclasses.Query

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        if not isinstance(query, dc.Query):
            raise TypeError(f"query arg must be of type {dc.Query}, got {type(query)}")
        document = self._private_request("GET", query.source_path())
        return dc.ApiResponse(**document)

    def create_query(
        self, data_source: str, query: list, name: str, slug: str, collection=None
    ) -> dc.Query:
        """Create a new query.

        :param str data_source: Source of the data either ``app`` or ``filterbar``.
        :param list query: Query that follows the specification described in |query_editor|.

         .. |query_editor| raw:: html

             <a href="https://clappformorg.github.io/" target="_blank">Query Editor</a>
        :param str name: Name for the query
        :param str slug: Internal identification string
        :param collection: Only required when the ``data_source`` argument holds the ``"app"``
            value.
        :type collection: clappform.dataclasses.Collection

        :returns: New Query object
        :rtype: clappform.dataclasses.Query
        """
        body = {"data_source": data_source, "query": query, "name": name, "slug": slug}
        if data_source == "app" and collection is None:
            raise TypeError(
                f"collection kwarg cannot be None when data_source is '{data_source}'"
            )
        if isinstance(collection, dc.Collection):
            body["app"] = collection.app
            body["collection"] = collection.slug
        document = self._private_request("POST", "/query", json=body)
        return dc.Query(**document["data"])

    def update_query(self, query: dc.Query) -> dc.Query:
        """Update an existing Query.

        :param query: Query object to update.
        :type query: clappform.dataclasses.Query

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> query = c.get_query("foo")
            >>> query.name = "Bar Query"
            >>> query = c.update_query(query)

        :returns: Updated Query object
        :rtype: clappform.dataclasses.Query
        """
        if not isinstance(query, dc.Query):
            raise TypeError(f"query arg must be of type {dc.Query}, got {type(query)}")
        document = self._private_request("PUT", query.path(), json=asdict(query))
        return dc.Query(**document["data"])

    def delete_query(self, query) -> dc.ApiResponse:
        """Delete a Query.

        :param query: Query identifier
        :type query: :class:`str` | :class:`clappform.dataclasses.Query`

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        path = self._query_path(query)
        document = self._private_request("DELETE", path)
        return dc.ApiResponse(**document)

    def aggregate_dataframe(self, options: dict, interval_timeout=0.1):
        """Aggregate a dataframe

        :param dict options: Options for dataframe aggregation.

        :returns: Generator to read dataframe
        :rtype: :class:`generator`
        """
        v = Validator(
            {
                "app": {"type": "string"},
                "collection": {"type": "string"},
                "type": {"type": "string"},
                "limit": {"min": 10, "max": 500},
                "sorting": {
                    "type": "dict",
                    "allow_unknown": True,
                    "schema": {
                        "ASC": {"type": "list"},
                        "DESC": {"type": "list"},
                    },
                },
                "search": {
                    "type": "dict",
                    "allow_unknown": True,
                    "schema": {
                        "input": {"type": "string"},
                        "keys": {"type": "list"},
                    },
                },
                "item_id": {
                    "type": "string",
                    "nullable": True,
                },
                "deep_dive": {"type": "dict"},
                "options": {"type": "list"},
                "inner_options": {"type": "list"},
            },
            require_all=True,
        )
        v.validate(options)

        path = "/dataframe/aggregate"
        params = {
            "method": "POST",
            "path": path,
            "json": v.document,
        }
        document = self._private_request(**params)
        pages_to_get = math.ceil(document["total"] / options["limit"])
        for _ in range(pages_to_get):
            for y in document["data"]:
                yield y
            params["path"] = f"{path}?next_page={document['next_page']}"
            time.sleep(interval_timeout)  # Prevent Denial Of Service (dos) flagging.
            document = self._private_request(**params)

    def read_dataframe(self, query, limit=100, interval_timeout=0.1):
        """Read a dataframe.

        :param query: Query to use on collection
        :type query: clappform.dataclasses.Collection
        :param int limit: Amount of records to retreive per request.
        :param interval_timeout: Time to sleep per request.
        :type interval_timeout: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform("https://app.clappform.com", "j.doe@clappform.com", "S3cr3tP4ssw0rd!")
            >>> query = c.get_query("foo")
            >>> it = c.read_dataframe(query)
            >>> for i in it:
            ...     print(i)

        :returns: Generator to read dataframe
        :rtype: :class:`generator`
        """
        if not isinstance(query, dc.Query):
            raise TypeError(f"query arg mgust be of type {dc.Query}, got {type(query)}")
        path = "/dataframe/read_data"
        params = {
            "method": "POST",
            "path": path,
            "json": {"query": query.slug, "limit": limit},
        }
        document = self._private_request(**params)
        if "total" not in document or document["total"] == 0:
            return
        pages_to_get = math.ceil(document["total"] / limit)
        for _ in range(pages_to_get):
            for y in document["data"]:
                yield y
            params["path"] = f"{path}?next_page={document['next_page']}"
            time.sleep(interval_timeout)  # Prevent Denial Of Service (dos) flagging.
            document = self._private_request(**params)

    def append_dataframe(self, collection, array: list[dict]) -> dc.ApiResponse:
        """Append data to a collection.

        :param collection: Collection to append data to.
        :type collection: clappform.dataclasses.Collection
        :param array: List of dictionary objects to append.
        :type array: list[dict]

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        if not isinstance(collection, dc.Collection):
            raise TypeError(
                f"collection arg must be of type {dc.Collection}, got {type(collection)}"
            )
        document = self._private_request("POST", collection.dataframe_path(), json=array)
        return dc.ApiResponse(**document)

    def sync_dataframe(self, collection, array: list[dict]) -> dc.ApiResponse:
        """Synchronize a dataframe.

        Synchronize replaces the existing data with data found in ``array``.

        :param collection: Collection to append data to.
        :type collection: clappform.dataclasses.Collection
        :param array: Is a list of dictionary objects.
        :type array: list[dict]

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        if not isinstance(collection, dc.Collection):
            raise TypeError(
                f"collection arg must be of type {dc.Collection}, got {type(collection)}"
            )
        document = self._private_request("PUT", collection.dataframe_path(), json=array)
        return dc.ApiResponse(**document)

    def empty_dataframe(self, collection) -> dc.ApiResponse:
        """Empty a dataframe.

        :param collection: Collection to append data to.
        :type collection: clappform.dataclasses.Collection

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        if not isinstance(collection, dc.Collection):
            raise TypeError(
                f"collection arg must be of type {dc.Collection}, got {type(collection)}"
            )
        document = self._private_request("DELETE", collection.dataframe_path())
        return dc.ApiResponse(**document)
