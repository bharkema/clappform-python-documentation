"""
Clappform API Wrapper
~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2022 Clappform B.V..
:license: MIT, see LICENSE for more details.
"""
__requires__ = ["requests==2.28.1", "Cerberus==1.3.4", "pandas==1.5.2"]
# Python Standard Library modules
from urllib.parse import urlparse
from dataclasses import asdict
import tempfile
import math
import time
import json

# PyPi modules
from cerberus import Validator
import requests as r
import pandas as pd
import numpy as np

# clappform Package imports.
from . import dataclasses as dc
from .exceptions import HTTPError

# Metadata
__version__ = "2.4.3"
__author__ = "Clappform B.V."
__email__ = "info@clappform.com"
__license__ = "MIT"
__doc__ = "Clappform Python API wrapper"


class Clappform:
    """:class:`Clappform <Clappform>` class is used to more easily interact with an
    Clappform environement through the API.

    :param str base_url: Base URL of a Clappform environment e.g.
        ``https://app.clappform.com``.
    :param str username: Username used in the authentication :meth:`auth <auth>`.
    :param str password: Password used in the authentication :meth:`auth <auth>`.
    :param int timeout: Optional HTTP request timeout in seconds, defaults to: ``2``.

    Most routes of the Clappform API require authentication. For the routes in the
    Clappform API that require authentication :class:`Clappform <Clappform>` will do
    the authentication for you.

    In the example below ``c.get_apps()`` uses a route which requires authentication.
    :class:`Clappform <Clappform>` does the authentication for you.

    Usage::

        >>> from clappform import Clappform
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> apps = c.get_apps()
        >>> for app in apps:
        ...     print(app.name)
    """

    _auth: dc.Auth = None

    def __init__(self, base_url: str, username: str, password: str, timeout: int = 2):
        self._base_url: str = f"{base_url}/api"

        #: Username to use in the :meth:`auth <auth>`
        self.username: str = username

        #: Password to use in the :meth:`auth <auth>`
        self.password: str = password

        #: HTTP request timeout in seconds.
        self.timeout: int = timeout

    def _default_user_agent(self) -> str:
        """Return a string with version of requests and clappform packages."""
        requests_ua = r.utils.default_user_agent()
        return f"clappform/{__version__} {requests_ua}"

    def _request(self, method: str, path: str, **kwargs):
        """Implements :class:`requests.request`."""
        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self._default_user_agent()
        resp = r.request(
            method,
            f"{self._base_url}{path}",
            headers=headers,
            timeout=self.timeout,
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
        """Sends an authentication request. Gets called whenever authentication is
        required.

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

    def _remove_nones(self, original: dict) -> dict:
        return {k: v for k, v in original.items() if v is not None}

    def _app_path(self, app, extended: bool = False) -> str:
        if isinstance(app, dc.App):
            return app.path(extended=extended)
        return dc.App.format_path(app, extended=extended)

    def get_apps(self) -> list[dc.App]:
        """Gets all apps.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> apps = c.get_apps()

        :returns: List of :class:`clappform.dataclasses.App` or empty list if there are
            no apps.
        :rtype: list[clappform.dataclasses.App]
        """
        document = self._private_request("GET", "/apps")
        return [dc.App(**obj) for obj in document["data"]]

    def get_app(self, app, extended: bool = False) -> dc.App:
        """Get a single app.

        :param app: App to get from the API
        :type app: :class:`str` | :class:`clappform.dataclasses.App`
        :param bool extended: Optional retreive fully expanded app, defaults
            to ``false``.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
            >>> app = c.get_app("clappform")
            >>> app = c.get_app(app)

        :returns: App Object
        :rtype: clappform.dataclasses.App
        """
        path = self._app_path(app, extended)
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
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
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
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> app = c.get_app("foo")
            >>> app.name = "Bar"
            >>> app = c.update_app(app)

        :returns: Updated app object
        :rtype: clappform.dataclasses.App
        """
        if not isinstance(app, dc.App):
            raise TypeError(f"app arg is not of type {dc.App}, got {type(app)}")
        payload = self._remove_nones(asdict(app))
        document = self._private_request("PUT", app.path(), json=payload)
        return dc.App(**document["data"])

    def delete_app(self, app) -> dc.ApiResponse:
        """Delete an app.

        :param app: App to delete from the API
        :type app: :class:`str` | :class:`clappform.dataclasses.App`

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
            >>> c.delete_app("foo")

        :returns: Response from the API
        :rtype: clappform.dataclasses.ApiResponse
        """
        path = self._app_path(app)
        document = self._private_request("DELETE", path)
        return dc.ApiResponse(**document)

    def _collection_path(self, app, collection, extended: int = 0):
        if isinstance(collection, dc.Collection):
            return collection.path(extended=extended)
        if isinstance(app, dc.App):
            return dc.Collection.format_path(app.id, collection, extended=extended)
        return dc.Collection.format_path(app, collection, extended=extended)

    def get_collections(self, app=None, extended: int = 0) -> list[dc.Collection]:
        """Get all the collections.

        The `extended` parameter allows an integer value from 0 - 3.

        :param app: Optional return only collections from specified app, default:
            ``None``.
        :type app: clappform.dataclasses.Collection
        :param extended: Optional level of detail for each collection, default:
            ``0``.
        :type extended: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> app = c.get_app("foo")
            >>> collections = c.get_collections(extended=3)
            >>> collections = c.get_collections(app=app)

        :raises ValueError: extended value not in [0, 1, 2 ,3]

        :returns: List of Collections or empty list if there are no collections
        :rtype: list[clappform.dataclasses.Collection]
        """
        dc.Collection.check_extended(extended)
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
        :param offset: Offset from which to retreive items, only useful when extended
            is ``3``.
        :type offset: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> app = c.get_app("foo")
            >>> collection = c.get_collection("bar", app=app)
            >>> collection = c.get_collection("bar", app="foo")
            >>> collection = c.get_collection(collection)

        The :class:`TypeError` is only raised when ``collection`` parameter is of type
            :class:`str`
        and ``app`` parameter is ``None``.

        :raises ValueError: extended value not in [0, 1, 2 ,3]
        :raises TypeError: app kwargs must be of type
           :class:`clappform.dataclasses.App` or :class:`str`.

        :returns: Collection Object
        :rtype: clappform.dataclasses.Collection
        """
        if isinstance(collection, str) and app is None:
            t = type(collection)
            raise TypeError(
                f"app kwarg cannot be {type(app)} when collection arg is {t}"
            )
        path = self._collection_path(app, collection, extended)
        document = self._private_request("GET", f"{path}?offset={offset}")
        return dc.Collection(**document["data"])

    def create_collection(
        self, app, slug: str, name: str, desc: str, db: str = "MONGO"
    ) -> dc.Collection:
        """Create a new Collection.

        :param app: App identifier to create collection for.
        :type app: :class:`str` | :class:`clappform.dataclasses.App`.
        :param str slug: Name used for internal identification.
        :param str name: Name of the collection.
        :param str desc: Description of what data the collection holds.
        :param str db: Database where collection is stored. Valid values for ``db`` are
            ``MONGO`` and ``DATALAKE``, defaults to: ``MONGO``

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> app = c.get_app("foo")
            >>> new_collection = c.create_collection(
            ...     app,
            ...     "bar",
            ...     "Bar",
            ...     "Bar Collection"
            ... )

        :returns: New Collection Object
        :rtype: clappform.dataclasses.Collection
        """
        if isinstance(app, dc.App):
            path = app.collection_path()
        elif isinstance(app, str):
            path = dc.App.format_collection_path(app)
        else:
            raise TypeError(f"app is not of type {dc.App} or {str}, got {type(app)}")

        valid_databases = ("MONGO", "DATALAKE")
        if db not in valid_databases:
            raise ValueError(f"db kwarg value is not one of: {valid_databases}")
        document = self._private_request(
            "POST",
            path,
            json={
                "slug": slug,
                "name": name,
                "description": desc,
                "database": db,
            },
        )
        return dc.Collection(**document["data"])

    def update_collection(self, collection: dc.Collection) -> dc.Collection:
        """Update an existing collection.

        :param collection: Collection object to update
        :type collection: clappform.dataclasses.Collection

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
            >>> collection = c.get_collection("bar", app="foo")
            >>> collection.name = "Spam & Eggs Collection"
            >>> collection = c.update_collection(collection)

        :raises TypeError: collection arg is not of type
            :class:`clappform.dataclasses.Collection`

        :returns: Updated Collection object
        :rtype: clappform.dataclasses.Collection
        """
        if not isinstance(collection, dc.Collection):
            t = type(collection)
            raise TypeError(f"collection arg is not of type {dc.Collection}, got {t}")
        payload = self._remove_nones(asdict(collection))
        document = self._private_request("PUT", collection.path(), json=payload)
        return dc.Collection(**document["data"])

    def delete_collection(self, collection: dc.Collection) -> dc.ApiResponse:
        """Delete a collection.

        :param collection: Collection to remove
        :type collection: clappform.dataclasses.Collection

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
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
        return dc.Query.format_path(query)

    def get_queries(self) -> list[dc.Query]:
        """Get all queries.

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
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
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
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
        :param list query: Query that follows the specification described in
            |query_editor|.

         .. |query_editor| raw:: html

             <a href="https://clappformorg.github.io/" target="_blank">Query Editor</a>
        :param str name: Name for the query
        :param str slug: Internal identification string
        :param collection: Only required when the ``data_source`` argument holds the
            ``"app"`` value.
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
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
            >>> query = c.get_query("foo")
            >>> query.name = "Bar Query"
            >>> query = c.update_query(query)

        :returns: Updated Query object
        :rtype: clappform.dataclasses.Query
        """
        if not isinstance(query, dc.Query):
            raise TypeError(f"query arg must be of type {dc.Query}, got {type(query)}")
        payload = self._remove_nones(asdict(query))
        document = self._private_request("PUT", query.path(), json=payload)
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

    def aggregate_dataframe(self, options: dict, interval_timeout: int = 0.1):
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

    def read_dataframe(self, query, limit: int = 100, interval_timeout: int = 0.1):
        """Read a dataframe.

        :param query: Query to for retreiving data. When Query is of type
            :class:`clappform.dataclasses.Collection` everything inside the collection
            is retreived.
        :type query: :class:`clappform.dataclasses.Query` |
            :class:`clappform.dataclasses.Collection`
        :param int limit: Amount of records to retreive per request.
        :param interval_timeout: Optional time to sleep per request, defaults to:
            ``0.1``.
        :type interval_timeout: int

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!"
            ... )
            >>> query = c.get_query("foo")
            >>> it = c.read_dataframe(query)
            >>> for i in it:
            ...     print(i)

        :returns: Generator to read dataframe
        :rtype: :class:`generator`
        """
        path = "/dataframe/read_data"
        params = {
            "method": "POST",
            "path": f"{path}?extended=true",
            "json": {"limit": limit},
        }
        if isinstance(query, dc.Query):
            params["json"]["query"] = query.slug
        elif isinstance(query, dc.Collection):
            params["json"]["app"] = query.app
            params["json"]["collection"] = query.slug
        else:
            t = type(query)
            raise TypeError(
                f"query arg must be of type {dc.Query} or {dc.Collection}, got {t}"
            )

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

    def write_dataframe(
        self,
        df: pd.DataFrame,
        collection: dc.Collection,
        chunk_size: int = 100,
        interval_timeout: int = 0.1,
    ):
        """Write Pandas DataFrame to collection.

        :param df: Pandas DataFrame to write to collection
        :type df: :class:`pandas.DataFrame`
        :param collection: Collection to hold DataFrame records
        :type collection: :class:`clappform.dataclasses.Collection`
        :param int chunk_size: defaults to: ``100``
        :param interval_timeout: Optional time to sleep per request, defaults to:
            ``0.1``.
        :type interval_timeout: int
        """
        # Transform DataFrame to be JSON serializable
        for col in df.columns:
            if df[col].dtype == "datetime64[ns, UTC]":
                df[col] = df[col].astype("datetime64[s, UTC]").astype("int")
            df[col] = df[col].replace([np.nan, np.inf, -np.inf], None)
        df = df.replace([np.nan, np.inf, -np.inf], None)

        # Split DataFrame up into chunks.
        list_df = [df[i : i + chunk_size] for i in range(0, df.shape[0], chunk_size)]
        for i in range(len(list_df)):
            # `TemporaryFile` And `force_ascii=False` force the chunck to be `UTF-8`
            # encoded.
            with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fd:
                df.to_json(fd, orient="records", force_ascii=False)
                fd.seek(0)  # Reset pointer to begin of file for reading.
                data = json.loads(fd.read())
            self.append_dataframe(collection, data)
            time.sleep(interval_timeout)

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
            t = type(collection)
            raise TypeError(f"collection arg must be of type {dc.Collection}, got {t}")
        document = self._private_request(
            "POST", collection.dataframe_path(), json=array
        )
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
            t = type(collection)
            raise TypeError(f"collection arg must be of type {dc.Collection}, got {t}")
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
            t = type(collection)
            raise TypeError(f"collection arg must be of type {dc.Collection}, got {t}")
        document = self._private_request("DELETE", collection.dataframe_path())
        return dc.ApiResponse(**document)

    def _actionflow_path(self, actionflow) -> str:
        if isinstance(actionflow, dc.Actionflow):
            return actionflow.path()
        return dc.Actionflow.format_path(actionflow)

    def get_actionflows(self) -> list[dc.Actionflow]:
        """Get all actionflows.

        :returns: List of :class:`clappform.dataclasses.Actionflow` or empty list if
            there are no actionflows.
        :rtype: list[clappform.dataclasses.Actionflow]
        """
        document = self._private_request("GET", "/actionflows")
        return [dc.Actionflow(**obj) for obj in document["data"]]

    def get_actionflow(self, actionflow) -> dc.Actionflow:
        """Get single actionflow.

        :param actionflow: Actionflow to get from the API
        :type actionflow: :class:`int` | :class:`clappform.dataclasses.App`

        Usage::

            >>> from clappform import Clappform
            >>> c = Clappform(
            ...     "https://app.clappform.com",
            ...     "j.doe@clappform.com",
            ...     "S3cr3tP4ssw0rd!",
            ... )
            >>> af = c.get_actionflow(1)
            >>> af = c.get_actionflow(af)

        :returns: Actionflow Object
        :rtype: clappform.dataclasses.Actionflow
        """
        path = self._actionflow_path(actionflow)
        document = self._private_request("GET", path)
        return dc.Actionflow(**document["data"])

    def create_actionflow(self, name: str, settings: dict) -> dc.Actionflow:
        """Create a new actionflow.

        :param str name: Display name for the new actionflow.
        :param dict settings: Settings object

        :returns: New Actionflow object
        :rtype: clappform.dataclasses.Actionflow
        """
        document = self._private_request(
            "POST",
            "/actionflow",
            json={
                "name": name,
                "settings": settings,
            },
        )
        return dc.Actionflow(**document["data"])

    def update_actionflow(self, actionflow: dc.Actionflow) -> dc.Actionflow:
        """Update an existing Actionflow.

        :param actionflow: Actionflow object to update.
        :type actionflow: clappform.dataclasses.Actionflow

        :returns: Updated Actionflow object
        :rtype: clappform.dataclasses.Actionflow
        """
        if not isinstance(actionflow, dc.Actionflow):
            raise TypeError(
                f"actionflow arg is not of type {dc.Actionflow}, got {type(actionflow)}"
            )
        payload = self._remove_nones(asdict(actionflow))
        document = self._private_request("PUT", actionflow.path(), json=payload)
        return dc.Actionflow(**document["data"])

    def delete_actionflow(self, actionflow) -> dc.ApiResponse:
        """Delete a Actionflow.

        :param actionflow: Actionflow identifier
        :type actionflow: :class:`int` | :class:`clappform.dataclasses.Actionflow`

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        path = self._actionflow_path(actionflow)
        document = self._private_request("DELETE", path)
        return dc.ApiResponse(**document)

    def _questionnaire_path(self, questionnaire, extended: bool = False) -> str:
        if isinstance(questionnaire, dc.Questionnaire):
            return questionnaire.path(extended=extended)
        return dc.Questionnaire.format_path(questionnaire, extended=extended)

    def get_questionnaires(self, extended: bool = False) -> list[dc.Questionnaire]:
        """Get all questionnaires

        :param bool extended: Optional retreive fully expanded questionnaires, defaults
            to ``false``.

        :returns: List of :class:`clappform.dataclasses.Questionnaire` or empty list if
            there are no questionnaires.
        :rtype: list[clappform.dataclasses.Questionnaire]
        """
        if not isinstance(extended, bool):
            raise TypeError(f"extended is not of type {bool}, got {type(extended)}")
        extended = str(extended).lower()
        document = self._private_request("GET", f"/questionnaires?extended={extended}")
        return [dc.Questionnaire(**obj) for obj in document["data"]]

    def get_questionnaire(
        self, questionnaire, extended: bool = False
    ) -> dc.Questionnaire:
        """Get a questionnaire

        :param bool extended: Optional retreive fully expanded questionnaire, defaults
            to ``false``.

        :returns: Qustionnaire Object
        :rtype: clappform.dataclasses.Questionnaire
        """
        path = self._questionnaire_path(questionnaire, extended=extended)
        document = self._private_request("GET", path)
        return dc.Questionnaire(**document["data"])

    def create_questionnaire(self, name: str, settings: dict) -> dc.ApiResponse:
        """Create a new questionnaire.

        :param str name: Display name for the new questionnaire.
        :param dict settings: Settings object

        :returns: ApiResponse object
        :rtype: clappform.dataclasses.ApiResponse
        """
        document = self._private_request(
            "POST",
            "/questionnaire",
            json={
                "name": name,
                "settings": settings,
            },
        )
        return dc.ApiResponse(**document)

    def update_questionnaire(
        self, questionnaire: dc.Questionnaire, settings: dict
    ) -> dc.Questionnaire:
        """Update an existing Questionnaire.

        :param questionnaire: Questionnaire object to update.
        :type questionnaire: clappform.dataclasses.Questionnaire
        :param dict settings: Settings object

        :returns: Updated Questionnaire object
        :rtype: clappform.dataclasses.Questionnaire
        """
        if not isinstance(questionnaire, dc.Questionnaire):
            t = type(questionnaire)
            raise TypeError(
                f"questionnaire arg must be of type {dc.Questionnaire}, got {t}"
            )
        payload = self._remove_nones(
            {
                "active": questionnaire.active,
                "settings": settings,
            }
        )
        document = self._private_request(
            "PUT",
            questionnaire.path(),
            json=payload,
        )
        return dc.Questionnaire(**document["data"])

    def delete_questionnaire(self, questionnaire):
        """Delete a Questionnaire.

        :param questionnaire: Questionnaire identifier
        :type questionnaire: :class:`int` |
            :class:`clappform.dataclasses.Questionnaire`

        :returns: API response object
        :rtype: clappform.dataclasses.ApiResponse
        """
        path = self._questionnaire_path(questionnaire)
        document = self._private_request("DELETE", path)
        return dc.ApiResponse(**document)

    def _export_actions_from_groups(self, groups: list[dict]) -> list[dict]:
        actions = []
        for group in groups:
            for page in group["pages"]:
                for row in page["rows"]:
                    for module in row["modules"]:
                        if "actions" not in module["selection"]:
                            continue
                        for action in module["selection"]["actions"]:
                            actions.append(action)
        return actions

    def export_app(self, app) -> dict:
        """Export an app.

        :param app: App to export
        :type app: :class:`str` | :class:`clappform.dataclasses.App`

        :returns: Exported App
        :rtype: dict
        """
        app = self.get_app(app, extended=True)
        actions = self._export_actions_from_groups(app.groups)

        actionflows = [
            self.get_actionflow(x["actionflowId"]["id"])
            for x in filter(
                lambda x: "type" in x
                and x["type"] == "actionflow"
                and "actionflowId" in x
                and x["actionflowId"] is not None
                and "id" in x["actionflowId"],
                actions,
            )
        ]
        questionnaires = [
            self.get_questionnaire(x["template"]["id"])
            for x in filter(
                lambda x: "type" in x
                and x["type"] == "questionnaire"
                and "template" in x
                and x["template"] is not None
                and "id" in x["template"],
                actions,
            )
        ]
        import_entries_document = self._private_request("GET", "/import?extended=true")
        # Non-iterable value `app.collections` is used in an iterating context
        # (not-an-iterable). `extended=True` In `self.get_app` will change
        # `dc.App.collections` to a `list`.
        # pylint: disable=E1133
        import_entries = list(
            filter(
                lambda x: x["collection"] in [x["slug"] for x in app.collections],
                import_entries_document["data"],
            )
        )
        # pylint: enable=E1133
        version = self.version()
        return {
            "apps": [asdict(app)],
            "collections": app.collections,
            "form_templates": [asdict(x) for x in questionnaires],
            "action_flows": [asdict(x) for x in actionflows],
            "import_entry": import_entries,
            "config": {
                "timestamp": int(time.time()),
                "created_by": self.username,
                "enviroment": urlparse(self._base_url).hostname,
                "api_version": version.api,
                "web_application_version": version.web_application,
                "web_server_version": version.web_server,
                "deployable": True,
            },
        }

    def import_app(self, app: dict, data_export: bool = False) -> dc.ApiResponse:
        """Import an app.

        :param dict app: Exported app object.

        :returns: Api Response Object
        :rtype: clappform.dataclasses.ApiResponse
        """
        config = app.pop("config")
        if not config["deployable"]:
            # pylint: disable=W0719
            raise Exception("app is not deployable")
        # pylint: enable=W0719

        if not isinstance(data_export, bool):
            t = type(data_export)
            raise TypeError(f"data_export is not of type {bool}, got {t}")
        app["delete_mongo_data"] = data_export
        document = self._private_request("POST", "/transfer/app", json=app)
        return dc.ApiResponse(**document)
