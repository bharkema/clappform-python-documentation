"""
clappform.dataclasses
~~~~~~~~~~~~~~~~~~~~~

This module contains the set of Clappform's return objects.
"""
# Python Standard Library modules
from dataclasses import dataclass, field
import base64
import json
import time


@dataclass
class ApiResponse:
    """Data class to represent generic API response.

    :param int code: HTTP status code.
    :param str message: Message about the request and response.
    :param str response_id: Response Id can be used to open support ticket.
    """

    #: HTTP status code.
    code: int
    #: Message about the request and response.
    message: str
    #: Response Id can be used to open support ticket.
    response_id: str

    def __init__(self, code: int, message: str, response_id: str, **kwargs):
        self.code = code
        self.message = message
        self.response_id = response_id
        for key, value in kwargs.items():
            setattr(self, key, value)


@dataclass
class Auth:
    """Authentication dataclass.

    :param str access_token: Bearer token to be used in a HTTP authorization header.
    :param int refresh_expiration: Integer representing the when the
        :attr:`refresh_token` is invalid.
    :param str refresh_token: Bearer token to be used get new :attr:`access_token`.
    """

    #: Bearer token to be used in a HTTP authorization header.
    access_token: str
    #: Integer representing the when the :attr:`refresh_token` is invalid.
    refresh_expiration: int
    #: Bearer token to be used get new :attr:`access_token`.
    refresh_token: str

    def is_token_valid(self) -> bool:
        """Returns boolean answer to: is the :attr:`access_token` still valid?

        :returns: Validity of :attr:`access_token`
        :rtype: bool
        """
        token_data = json.loads(
            base64.b64decode(self.access_token.split(".")[1] + "==")
        )
        if token_data["exp"] + 60 > int(time.time()):
            return True
        return False


@dataclass
class Version:
    """Version dataclass.

    :param str api: Version of the API.
    :param str web_application: Version of the Web Application.
    :param str web_server: Version of the Web Server
    """

    #: Version of the API.
    api: str
    #: Version of the Web Application.
    web_application: str
    #: Version of the Web Server
    web_server: str


@dataclass
class App:
    """App dataclass.

    :param int collections: Number of collections this app has.
    :param str default_page: Page to view when opening app.
    :param str description: Description below app name.
    :param int groups: Nuber of groups in an app.
    :param str id: Used internally to identify app.
    :param str name: Name of the app.
    :param dict settings: Settings to configure app.
    """

    collections: int
    default_page: str
    description: str
    groups: int
    id: str
    name: str
    settings: dict
    _path: str = field(init=False, repr=False, default="/app/{0}")

    def path(self) -> str:
        """Return the route used to retreive the App.

        :returns: App API route
        :rtype: str
        """
        return self._path.format(self.id)


@dataclass
class Collection:
    """Collection dataclass."""

    app: str
    database: str
    name: str
    slug: str
    items: int = None
    description: str = None
    is_encrypted: bool = None
    is_locked: bool = None
    is_logged: bool = None
    queries: list = None
    sources: list = None
    id: int = None
    _path: str = field(init=False, repr=False, default="/collection/{0}/{1}")

    def path(self) -> str:
        """Return the route used to retreive the Collection.

        :returns: Collection API route
        :rtype: str
        """
        return self._path.format(self.app, self.slug)

    def dataframe_path(self) -> str:
        """Return the route used to retreive the Dataframe.

        :returns: Dataframe API route
        :rtype: str
        """
        return f"/dataframe/{self.app}/{self.slug}"


@dataclass
class Query:
    """Query dataclass."""

    app: str
    collection: str
    data_source: str
    export: bool
    id: int
    name: str
    query: list
    slug: str
    source_query: str
    modules: list = None
    _path: str = field(init=False, repr=False, default="/query/{0}")

    def path(self) -> str:
        """Return the route used to retreive the Query.

        :returns: Query API route
        :rtype: str
        """
        return self._path.format(self.slug)

    def source_path(self) -> str:
        """Return the route used to source the Query.

        :returns: Source Query API route
        :rtype: str
        """
        return f"/source_query/{self.slug}"


@dataclass
class Actionflow:
    """Actionflow dataclass."""

    id: int
    name: str
    settings: dict
    cronjobs: list = None
    tasks: list = None
    _path: str = field(init=False, repr=False, default="/actionflow/{0}")

    def path(self) -> str:
        """Return the route used to retreive the Actionflow.

        :returns: Actionflow API route
        :rtype: str
        """
        return self._path.format(self.id)


@dataclass
class Questionnaire:
    """Questionnaire dataclass."""

    name: str
    id: int
    created_at: int
    active: bool
    created_by: dict
    latest_version: dict
    versions: list = None
    _path: str = field(init=False, repr=False, default="/questionnaire/{0}")

    def path(self) -> str:
        """Return the route used to retreive the Questionnaire.

        :returns: Questionnaire API route
        :rtype: str
        """
        return self._path.format(self.id)
