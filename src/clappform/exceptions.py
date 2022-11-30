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
