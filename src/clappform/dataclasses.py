"""
clappform.dataclasses
~~~~~~~~~~~~~~~~~~~~~

This module contains the set of Clappform's return objects.
"""
# Python Standard Library modules
from dataclasses import dataclass
import base64
import json
import time
import abc


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


class AbstractBase(metaclass=abc.ABCMeta):
    """AbstractBase is used as a base class for dataclasses.
    :class:`AbstractBase <AbstractBase>` contains only one abstract method. Any class
    that inherits from :class:`AbstractBase <AbstractBase>` is required to implement
    :meth:`path <path>`.
    """

    @abc.abstractmethod
    def path(self) -> str:
        """Return the route used to by the resource.

        :returns: HTTP path of the resource
        :rtype: str
        """
        return


@dataclass
class App(AbstractBase):
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

    @staticmethod
    def format_path(app: str, extended: bool = False) -> str:
        """Return the route used to retreive the App.

        :returns: App's HTTP resource path.
        :rtype: str
        """
        if not isinstance(app, str):
            raise TypeError(f"app is not of type {str}, got {type(app)}")
        if not isinstance(extended, bool):
            raise TypeError(f"extended is not of type {bool}, got {type(extended)}")
        extended = str(extended).lower()
        return f"/app/{app}?extended={extended}"

    @staticmethod
    def format_collection_path(app: str) -> str:
        """Return the base route used to get and create the App's collections'.

        :returns: App's collection HTTP get and create path.
        :rtype: str
        """
        App.format_path(app)  # Checks if `app` is of type `str`.
        return f"/collection/{app}"

    def path(self, extended: bool = False) -> str:
        """Return the route used to retreive the App.

        :returns: App's HTTP resource path.
        :rtype: str
        """
        return App.format_path(self.id, extended)

    def collection_path(self) -> str:
        """Return the base route used to get and create the App's collections'.

        :returns: App's collection HTTP get and create path.
        :rtype: str
        """
        return App.format_collection_path(self.id)


@dataclass
class Collection(AbstractBase):
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

    @staticmethod
    def check_extended(extended: int):
        """Check if ``extended`` is of type :class:`int` and `0` to `3`."""
        if not isinstance(extended, int):
            raise TypeError(f"extended is not of type {int}, got {type(extended)}")
        extended_range = range(4)  # API allows for 4 levels of extension.
        if extended not in extended_range:
            raise ValueError(f"extended {extended} not in {list(extended_range)}")

    @staticmethod
    def format_base_path(app: str, extended: int = 0) -> str:
        """Return the route used for getting all and creating collections.

        :returns: Collection getting and creating HTTP path
        :rtype: str
        """
        App.path(app)  # This call checks if app is of type str.
        Collection.check_extended(extended)
        return f"/collection/{app}?extended={extended}"

    def base_path(self, extended: int = 0) -> str:
        """Return the route used for getting all and creating collections.

        :returns: Collection getting and creating HTTP path
        :rtype: str
        """
        return Collection.format_base_path(self.app, extended)

    @staticmethod
    def format_path(app: str, collection: str, extended: int = 0) -> str:
        """Return the route used to retreive the collection.

        :param str app: App to which collection belongs to.
        :param str collection: Collection to get from app.
        :param int extended: Optional level to which the fields get expanded, defaults
            to: ``0``

        :returns: Collection's HTTP resouce path
        :rtype: str
        """
        path = Collection.format_base_path(app)  # Checks if `app` is of type `str`.
        if not isinstance(collection, str):
            raise TypeError(f"collection is not of type {str}, got {type(collection)}")
        Collection.check_extended(extended)
        return f"{path}/{collection}?extended={extended}"

    def path(self, extended: int = 0) -> str:
        """Return the route used to retreive the Collection.

        :param int extended: Level to which the fields get expanded.

        :returns: Collection API route
        :rtype: str
        """
        return Collection.format_path(self.app, self.slug, extended)

    def dataframe_path(self) -> str:
        """Return the route used to retreive the Dataframe.

        :returns: Collection's Dataframe HTTP resource path
        :rtype: str
        """
        return f"/dataframe/{self.app}/{self.slug}"


@dataclass
class Query(AbstractBase):
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

    @staticmethod
    def format_path(query: str) -> str:
        """Return the route used to retreive the Query.

        :returns: Query HTTP resource path
        :rtype: str
        """
        if not isinstance(query, str):
            raise TypeError(f"query is not of type {str}, got {type(query)}")
        return f"/query/{query}"

    def path(self) -> str:
        """Return the route used to retreive the Query.

        :returns: Query HTTP resource path
        :rtype: str
        """
        return Query.format_path(self.slug)

    def source_path(self) -> str:
        """Return the route used to source the Query.

        :returns: Source Query API route
        :rtype: str
        """
        return f"/source_query/{self.slug}"


@dataclass
class Actionflow(AbstractBase):
    """Actionflow dataclass."""

    id: int
    name: str
    settings: dict
    cronjobs: list = None
    tasks: list = None

    @staticmethod
    def format_path(actionflow: int) -> str:
        """Return the route used to retreive the Actionflow.

        :param int actionflow: Actionflow id.

        :returns: Actionflow HTTP resource path
        :rtype: str
        """
        if not isinstance(actionflow, int):
            raise TypeError(f"actionflow is not of type {int}, got {type(actionflow)}")
        return f"/actionflow/{actionflow}"

    def path(self) -> str:
        """Return the route used to retreive the Actionflow.

        :returns: Actionflow HTTP resource path
        :rtype: str
        """
        return Actionflow.format_path(self.id)


@dataclass
class Questionnaire(AbstractBase):
    """Questionnaire dataclass."""

    name: str
    id: int
    created_at: int
    active: bool
    created_by: dict
    latest_version: dict
    versions: list = None

    @staticmethod
    def format_path(questionnaire: int, extended: bool = False) -> str:
        """Return the route used to retreive the Questionnaire.

        :param int questionnaire: Questionnaire id.
        :param bool extended: Include versions when retreiving questionnaire.

        :returns: Questionnaire HTTP resource path
        :rtype: str
        """
        if not isinstance(questionnaire, int):
            t = type(questionnaire)
            raise TypeError(f"questionnaire is not of type {int}, got {t}")
        if not isinstance(extended, bool):
            raise TypeError(f"extended is not of type {bool}, got {type(extended)}")
        extended = str(extended).lower()
        return f"/questionnaire/{questionnaire}?extended={extended}"

    def path(self, extended: bool = False) -> str:
        """Return the route used to retreive the Questionnaire.

        :param bool extended: Include versions when retreiving questionnaire.

        :returns: Questionnaire API route
        :rtype: str
        """
        return Questionnaire.format_path(self.id, extended=extended)
