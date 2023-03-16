"""
play1
"""

from airtight.cli import configure_commandline
import logging
from validators import url as valid_uri

logger = logging.getLogger(__name__)

DEFAULT_LOG_LEVEL = logging.WARNING
OPTIONAL_ARGUMENTS = [
    [
        "-l",
        "--loglevel",
        "NOTSET",
        "desired logging level ("
        + "case-insensitive string: DEBUG, INFO, WARNING, or ERROR",
        False,
    ],
    ["-v", "--verbose", False, "verbose output (logging level == INFO)", False],
    [
        "-w",
        "--veryverbose",
        False,
        "very verbose output (logging level == DEBUG)",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["start_id", str, "Pleiades URI to start with"]
]
BASE_URI = "https://pleiades.stoa.org/places/"


def raise_invalid_uri(v):
    raise ValueError(f"Invalid Pleiades URI or ID: {v}")


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    id = kwargs["start_id"]
    while True:
        if not (valid_uri(id)):
            try:
                int(id)
            except ValueError:
                raise_invalid_uri(kwargs["start_id"])
            else:
                id = BASE_URI + id
        elif not id.startswith(BASE_URI):
            raise_invalid_uri(kwargs["start_id"])
        else:
            break


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
