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

    _expires: int

    def __init__(self, access_token: str, refresh_expiration: int, refresh_token: str):
        self.access_token = access_token
        self.refresh_expiration = refresh_expiration
        self.refresh_token = refresh_token

        token_data = json.loads(
            base64.b64decode(self.access_token.split(".")[1] + "==")
        )
        self._expires = token_data["exp"]

    def is_token_valid(self) -> bool:
        """Returns boolean answer to: is the :attr:`access_token` still valid?

        :returns: Validity of :attr:`access_token`
        :rtype: bool
        """
        if self._expires > int(time.time()) + 60:
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
    api: str = None

    #: Version of the Web Application.
    web_application: str = None

    #: Version of the Web Server
    web_server: str = None

    def one_or_all_path(self) -> str:
        """Return the path to retreive the version.

        :returns: Version HTTP path
        :rtype: str
        """
        return "/version"


class ResourceType(metaclass=abc.ABCMeta):
    """ResourceType is used as an interface for :class:`clappform.Clappform`. Any class
    that uses this class as a base can be used with :class:`clappform.Clappform`'s
    methods.
    """

    @staticmethod
    def bool_to_lower(boolean: bool) -> str:
        """Return a boolean string in lowercase.

        :param boolean: ``True`` or ``False`` value to convert to lowercase string.
        :type boolean: bool

        :returns: Lowercase boolean string
        :rtype: str
        """
        if not isinstance(boolean, bool):
            raise TypeError(f"boolean is not of type {bool}, got {type(boolean)}")
        return str(boolean).lower()

    @abc.abstractmethod
    def one_or_all_path(self) -> str:
        """Return the path to retreive one or all resources.

        :returns: Resource HTTP path
        :rtype: str
        """

    @abc.abstractmethod
    def one_path(self) -> str:
        """Return the path to retreive this Resource

        :returns: Resource HTTP path
        :rtype: str
        """

    @abc.abstractmethod
    def all_path(self) -> str:
        """Return the path to retreive all Resources.

        :returns: Resource HTTP path
        :rtype: str
        """

    @abc.abstractmethod
    def create_path(self) -> str:
        """Return the path to create a Resource.

        :returns: Resource HTTP path
        :rtype: str
        """


@dataclass
class App(ResourceType):
    """App resource type.

    :param int collections: Number of collections this app has.
    :param str default_page: Page to view when opening app.
    :param str description: Description below app name.
    :param int groups: Nuber of groups in an app.
    :param str id: Used internally to identify app.
    :param str name: Name of the app.
    :param dict settings: Settings to configure app.
    :param bool extended: Whether fully expanded app object with ``get``.

    Usage::

        >>> from clappform import Clappform
        >>> import clappform.dataclasses as r
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> new_app = r.App(
        ...     id="uspresidents",
        ...     name="US Presidents",
        ...     description="US Presidents Dashboard",
        ...     settings={}
        ... )
        >>> c.create(new_app)
        App(collections=0, default_page='', description='US Presidents Dashboard', g...
        >>> app = c.get(r.App(id="uspresidents"))
        >>> c.delete(app)
        ApiResponse(code=200, message='Successfully deleted app with ID: uspresident...
        >>> for app in c.get(r.App()):
        ...     print(app.name)
    """

    #: Number of collections this app has. If ``extended=True`` this will be a list
    #: of collections.
    collections: int = None
    #: Slug of the page to display when opening the app.
    default_page: str = None
    #: Text under app name on the app overview page.
    description: str = None
    #: Groups of pages this app has. If ``extended=True`` this will be a list of dicts.
    groups: int = None
    #: String id of the app. This is also used in the URL as a slug.
    id: str = None
    _id: str = field(init=False, repr=False, default=None)
    #: Name of the app displayed on the page.
    name: str = None
    #: Extra settings that further configure the app.
    settings: dict = None
    #: Used by ``get`` to gauge whether to fetch fully expanded app object.
    extended: bool = field(init=True, repr=False, default=False)

    @property
    def id(self) -> str:
        """Return the id property.

        :returns: id Property
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        assert isinstance(value, (property, str, type(None)))
        if isinstance(value, property):
            value = self._id
        self._id = value

    def one_or_all_path(self) -> str:
        """Return the path to retreive one or all Apps.

        :returns: App HTTP path
        :rtype: str
        """
        if self.id is not None:
            return self.one_path()
        return self.all_path()

    def one_path(self) -> str:
        """Return the path to retreive this App

        :returns: App HTTP path
        :rtype: str
        """
        extended = self.bool_to_lower(bool(self.extended))
        if self.id is None:
            raise TypeError(f"id attribute can not be {None}")
        return f"/app/{self.id}?extended={extended}"

    def all_path(self) -> str:
        """Return the path to retreive all Apps.

        :returns: App HTTP path
        :rtype: str
        """
        extended = self.bool_to_lower(bool(self.extended))
        return f"/apps?extended={extended}"

    def create_path(self) -> str:
        """Return the path to create an App.

        :returns: App HTTP path
        :rtype: str
        """
        return "/app"


@dataclass
class Collection(ResourceType):
    """Collection resource type.

    :param str app: Id of the app collection belongs to.
    :param str slug: Unique id of the collection.
    :param str database: Database location to store documents, e.g. ``MONGO`` or
        ``DATALAKE``.
    :param str name: Display name of the collection.
    :param str description: Description below collection name. ``extended=1``
    :param int id: Numeric ID of the collection used for internal identification.
        ``extended=1``
    :param bool is_encrypted: Use of encryption on this collection. ``extended=1``
    :param bool is_locked: Read only permissions on collection. ``extended=1``
    :param bool is_logged: HTTP Access logging on this collection. ``extended=1``
    :param bool sources: List of locations the data originates from. ``extended=1``
    :param list queries: Queries that query this collection's data. ``extended=2``
    :param bool extended: At what level to expand collection object with ``get``.

    Usage::

        >>> from clappform import Clappform
        >>> import clappform.dataclasses as r
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> app = c.get(r.App(id="uspresidets"))
        >>> new_collection = r.Collection(
        ...     app=app,
        ...     database="MONGO",
        ...     name="United States Presidents",
        ...     slug="presidents",
        ...     description="All presidents of the United Stated of America"
        ... )
        >>> c.create(new_collection)
        Collection(app='uspresidents', slug='presidents', database='MONGO', name='Un...
        >>> collection = c.get(r.Collection(app="uspresidents", slug="presidents"))
        >>> c.delete(collection)
        ApiResponse(code=200, message='Successfully deleted collection with slug: pr...
        >>> for collection in c.get(r.Collection()):
        ...     print(f"{collection.app}: {collection.slug}")
    """

    #: App id this collection belong to. This can be of type
    #: :class:`clappform.dataclasses.App` or :class:`str`.
    app: str = None
    _app: str = field(init=False, repr=False, default=None)
    #: Unique string id for this collection.
    slug: str = None
    _slug: str = field(init=False, repr=False, default=None)
    #: Database location where this collection is stored, e.g. ``"MONGO"`` or
    #: ``"DATALAKE"``.
    database: str = None
    #: Name of the collection to display on the web page.
    name: str = None
    #: Description below the name to display on the web page.
    description: str = None
    #: Whether to use encryption for this collection. Default is ``False``.
    is_encrypted: bool = None
    #: Whether this collection is write protected. Collection is read only. Default is
    #: ``False``.
    is_locked: bool = None
    #: Whether HTTP access loggin is enabled. Default is ``False``.
    is_logged: bool = None
    #: Queries that have been created for this collection's data.
    queries: list = None
    #: List of location where the data in this collection came from.
    sources: list = None
    #: Numeric id of this collection, used for internal identifacation.
    id: int = None
    #: Used by ``get`` to gauge whether to fetch fully expanded app object. Allowed
    #: values: ``0`` - ``3``. Defaults to ``0``.
    extended: int = field(init=True, repr=False, default=0)

    @property
    def app(self) -> str:
        """Return the app property.

        :returns: app Property
        :rtype: str
        """
        return self._app

    @app.setter
    def app(self, value) -> None:
        assert isinstance(value, (property, str, App, type(None)))
        if isinstance(value, property):
            # initial value not specified, use default
            value = self._app
        if isinstance(value, App):
            value = value.id
        self._app = value

    @property
    def slug(self) -> str:
        """Return the slug property.

        :returns: slug Property
        :rtype: str
        """
        return self._slug

    @slug.setter
    def slug(self, value: str) -> None:
        assert isinstance(value, (property, str, type(None)))
        if isinstance(value, property):
            # initial value not specified, use default
            value = self._slug
        self._slug = value

    @staticmethod
    def check_extended(extended: int):
        """Check if ``extended`` is of type :class:`int` and `0` to `3`."""
        if not isinstance(extended, int):
            raise TypeError(f"extended is not of type {int}, got {type(extended)}")
        extended_range = range(4)  # API allows for 4 levels of extension.
        if extended not in extended_range:
            raise ValueError(f"extended {extended} not in {extended_range}")

    def one_or_all_path(self):
        """Return the path to retreive one or all collections.

        :returns: Collection HTTP path
        :rtype: str
        """
        if self.app is None and self.slug is None:
            return self.all_path()
        return self.one_path()

    def one_path(self) -> str:
        """Return the path to retreive this Collection

        :returns: Collection HTTP path
        :rtype: str
        """
        self.check_extended(self.extended)
        if self.app is None or self.slug is None:
            raise TypeError("both 'app' and 'slug' attributes can not be {None}")
        return f"/collection/{self.app}/{self.slug}?extended={self.extended}"

    def all_path(self) -> str:
        """Return the path to retreive all Collections.

        :returns: Collection HTTP path
        :rtype: str
        """
        self.check_extended(self.extended)
        return f"/collections?extended={self.extended}"

    def create_path(self) -> str:
        """Return the path to create a Collection.

        :returns: Collection HTTP path
        :rtype: str
        """
        if self.app is None:
            raise TypeError("app attribute can not be None")
        return f"/collection/{self.app}"

    def one_item_path(self, item: str) -> str:
        """Return the route used for creating and deleting items.

        :returns: Item HTTP path
        :rtype: str
        """
        if self.app is None or self.slug is None:
            raise TypeError("both 'app' and 'slug' attributes can not be {None}")
        if not isinstance(item, str):
            raise TypeError(f"item arg is not of type {str}, got {type(item)}")
        return f"/item/{self.app}/{self.slug}/{item}"

    def create_item_path(self) -> str:
        """Return the route used to create an item.

        :returns: Item HTTP path
        :rtype: str
        """
        if self.app is None or self.slug is None:
            raise TypeError(f"both 'app' and 'slug' attributes can not be {None}")
        return f"/item/{self.app}/{self.slug}"

    def dataframe_path(self) -> str:
        """Return the route used to retreive the Dataframe.

        :returns: Collection's Dataframe HTTP path
        :rtype: str
        """
        if self.app is None or self.slug is None:
            raise TypeError(f"'app' and 'slug' attributes can not be {None}")
        return f"/dataframe/{self.app}/{self.slug}"


@dataclass
class Query(ResourceType):
    """Collection resource type.

    Usage::

        >>> from clappform import Clappform
        >>> import clappform.dataclasses as r
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> collection = c.get(r.Collection(app="uspresidets", slug="presidents"))
        >>> new_query = r.Query(
        ...     collection=collection,
        ...     data_source="app",
        ...     query=[],
        ...     name="all presidents",
        ...     slug="f1cb2ba5-64a7-4056-99d5-7d639557970f",
        ... )
        >>> c.create(new_collection)
        Query(app='uspresidets', collection='presidents', data_source='app', export=...
        >>> query = c.get(r.Query(slug="f1cb2ba5-64a7-4056-99d5-7d639557970f"))
        >>> c.delete(query)
        ApiResponse(code=200, message='Successfully deleted query with slug: f1cb2ba...
        >>> for query in c.get(r.Query()):
        ...     print(f"{query.app}/{query.collection}: {query.slug}")
    """

    #: App id this query belong to. This can be of type
    #: :class:`clappform.dataclasses.App` or :class:`str`.
    app: str = None
    _app: str = field(init=False, repr=False, default=None)
    #: Collection slug this query refers to. This can be of type
    #: :class:`clappform.dataclasses.Collection` or :class:`str`.
    collection: str = None
    _collection: str = field(init=False, repr=False, default=None)
    data_source: str = None
    export: bool = None
    #: Numeric id used for internal identication
    id: int = None
    name: str = None
    query: list = None
    slug: str = None
    source_query: str = None
    modules: list = None
    primary: bool = None
    settings: dict = None

    @property
    def app(self) -> str:
        """Return the app property.

        :returns: app Property
        :rtype: str
        """
        return self._app

    @app.setter
    def app(self, value) -> None:
        assert isinstance(value, (property, str, App, type(None)))
        if isinstance(value, property):
            # initial value not specified, use default
            value = self._app
        if isinstance(value, App):
            value = value.id
        self._app = value

    @property
    def collection(self) -> str:
        """Return the collection property.

        :returns: collection Property
        :rtype: str
        """
        return self._collection

    @collection.setter
    def collection(self, value: str) -> None:
        assert isinstance(value, (property, str, Collection, type(None)))
        if isinstance(value, property):
            # initial value not specified, use default
            value = self._collection
        if isinstance(value, Collection):
            self._app = value.app
            value = value.slug
        self._collection = value

    def one_or_all_path(self) -> str:
        if self.slug is None:
            return self.all_path()
        return self.one_path()

    def one_path(self) -> str:
        """Return the route used to retreive the Query.

        :returns: Query HTTP resource path
        :rtype: str
        """
        if not isinstance(self.slug, str):
            raise TypeError(
                f"slug attribute is not of type {str}, got {type(self.slug)}"
            )
        return f"/query/{self.slug}"

    def all_path(self) -> str:
        """Return the route used to retreive the Query.

        :returns: Query HTTP resource path
        :rtype: str
        """
        return "/queries"

    def create_path(self) -> str:
        return "/query"

    def source_path(self) -> str:
        """Return the route used to source the Query.

        :returns: Source Query API route
        :rtype: str
        """
        if not isinstance(self.slug, str):
            raise TypeError(
                f"slug attribute is not of type {str}, got {type(self.slug)}"
            )
        return f"/source_query/{self.slug}"


@dataclass
class Actionflow(ResourceType):
    """Actionflow resource type.

    Usage::

        >>> from clappform import Clappform
        >>> import clappform.dataclasses as r
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> new_actionflow = r.Actionflow(
        ...     name="Periodic housekeeping",
        ...     settings={},
        ... )
        >>> c.create(new_collection)
        Actionflow(id=48, name='Periodic housekeeping', settings={}, cronjobs=None, ...
        >>> actionflow = c.get(r.Actionflow(id=48))
        >>> c.delete(actionflow)
        ApiResponse(code=200, message='Deleted action flow.', response_id='648083113...v
        >>> for af in c.get(r.Actionflow()):
        ...     print(f"{af.id}: {af.name}")
    """

    id: int = None
    name: str = None
    settings: dict = None
    cronjobs: list = None
    tasks: list = None

    def one_or_all_path(self) -> str:
        if self.id is None:
            return self.all_path()
        return self.one_path()

    def all_path(self) -> str:
        return "/actionflows"

    def one_path(self) -> str:
        return f"/actionflow/{self.id}"

    def create_path(self) -> str:
        return "/actionflow"


@dataclass
class Questionnaire(ResourceType):
    """Questionnaire dataclass."""

    name: str = None
    id: int = None
    created_at: int = None
    active: bool = None
    created_by: dict = None
    latest_version: dict = None
    versions: list = None
    settings: dict = field(init=True, repr=False, default=None)
    extended: bool = field(init=True, repr=False, default=False)

    def one_or_all_path(self) -> str:
        if self.id is None:
            return self.all_path()
        return self.one_path()

    def all_path(self) -> str:
        extended = self.bool_to_lower(bool(self.extended))
        return f"/questionnaires?extended={extended}"

    def one_path(self) -> str:
        extended = self.bool_to_lower(bool(self.extended))
        if not isinstance(self.id, int):
            raise TypeError(f"id attribute is not of type {int}, got {type(self.id)}")
        return f"/questionnaire/{self.id}?extended={extended}"

    def create_path(self) -> str:
        return "/questionnaire"


@dataclass
class User(ResourceType):
    """User resource type.

    Usage::

        >>> from clappform import Clappform
        >>> import clappform.dataclasses as r
        >>> c = Clappform(
        ...     "https://app.clappform.com",
        ...     "j.doe@clappform.com",
        ...     "S3cr3tP4ssw0rd!",
        ... )
        >>> user = c.get(r.User(email="j.doe@clappform.com")
        >>> new_user = r.User(
        ...     email="g.washington@clappform.com",
        ...     first_name="George",
        ...     last_name="Washington",
        ...     password="HavntGotWoodenTeeth",
        ... )
        >>> c.create(new_user)
        User(email='g.washington@clappform.com', extra_information={}, first_name='G...
        >>> query = c.get(r.Query(slug="f1cb2ba5-64a7-4056-99d5-7d639557970f"))
        >>> c.delete(query)
        ApiResponse(code=200, message='Successfully deactivated user, with email: g....
        >>> for user in c.get(r.User()):
        ...     print(f"{user.email}: {user.first_name} {user.last_name}")
    """

    #: Email address of the user.
    email: str = None
    #: Dictionary object describing extra related information about the user.
    extra_information: dict = None
    #: User's first name.
    first_name: str = None
    #: User's last name.
    last_name: str = None
    #: Whether user can authenticate or not.
    is_active: bool = None
    #: Numeric id used for internal identifaction.
    id: int = None
    #: User's phone number.
    phone: str = None
    #: Dictionary object containing notifications, emails, sms or whatsapp messages.
    #: ``extended=True``
    messages: dict = None
    #: Unix timestamp of when the user was last online. ``extended=True``
    last_online: int = None
    #: List of permissions this user has. ``extended=True``
    permissions: list[str] = None
    #: ``extended=True``
    roles: list[dict] = None
    #: Password of the user. Only used when creating a user.
    password: str = field(init=True, repr=False, default=None)
    #: Used by ``get`` to gauge whether to fetch fully expanded user object.
    extended: bool = field(init=True, repr=False, default=False)

    def one_or_all_path(self) -> str:
        """Return the path to retreive this User.

        :returns: User HTTP path
        :rtype: str
        """
        if self.email is None:
            return self.all_path()
        return self.one_path()

    def all_path(self) -> str:
        """Return the path to retreive all Users.

        :returns: User HTTP path
        :rtype: str
        """
        extended = self.bool_to_lower(bool(self.extended))
        return f"/users?extended={extended}"

    def one_path(self) -> str:
        """Return the path to retreive this User.

        :returns: User HTTP path
        :rtype: str
        """
        extended = self.bool_to_lower(bool(self.extended))
        if not isinstance(self.email, str):
            raise TypeError(
                f"email attribute is not of type {str}, got {type(self.email)}"
            )
        return f"/user/{self.email}?extended={extended}"

    def create_path(self) -> str:
        """Return the path to create a Collection.

        :returns: Collection HTTP path
        :rtype: str
        """
        return "/user"
