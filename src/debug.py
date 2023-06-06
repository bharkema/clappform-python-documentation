"""Script sets the python debugger and debug logging."""
# flake8: noqa=F401
# pylint: disable=W0611
import pdb
import logging
import clappform
import clappform.dataclasses as dc

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
