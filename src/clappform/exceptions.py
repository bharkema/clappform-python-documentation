"""
clappform.exceptions
~~~~~~~~~~~~~~~~~~~~

This module contains the set of Clappform's exceptions.
"""
# PyPi modules
import requests


class HTTPError(requests.exceptions.HTTPError):
    """An HTTP error occurred."""

    def __init__(self, *args, **kwargs):
        """Initialize HTTPError with `code`, `response_id`, `request` and `response`
        objects.
        """
        #: HTTP status code from JSON body.
        self.code: int = kwargs.pop("code", None)

        #: Response Id useful for support ticket.
        self.response_id: str = kwargs.pop("response_id", None)

        super().__init__(*args, **kwargs)


class PaginationError(requests.exceptions.HTTPError):
    """A pagination error in paginated response occurred."""

    def __init__(self, *args, **kwargs):
        """Initialize PaginationError with `data`, object."""
        #: Response JSON document.
        self.data: dict = kwargs.pop("data", None)

        super().__init__(*args, **kwargs)


class PaginationTotalError(PaginationError):
    """A total error in paginated response occurred."""

    def __init__(self, *args, **kwargs):
        """Initialize PaginationTotalError with `total`, object."""
        #: Total number of elements in collection.
        self.total: int = kwargs.pop("total", None)

        super().__init__(*args, **kwargs)


class PaginationKeyError(PaginationError):
    """A key error in paginated response occurred."""

    def __init__(self, *args, **kwargs):
        """Initialize PaginationKeyError with `missing_key`, object."""
        #: Key missing from the Response JSON document.
        self.missing_key: str = kwargs.pop("missing_key", None)

        super().__init__(*args, **kwargs)
