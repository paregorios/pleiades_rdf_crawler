#
# This script is part of the pleiades_rdf_crawler package
# https://github.com/paregorios/pleiades_rdf_crawler
#
# By Tom Elliott
# https://orcid.org/0000-0002-4114-66773
#
# Copyright 2023 New York University (non-faculty employee compensated work)
# GNU Affero General Public License (see LICENSE file)
#
"""
Get all connected places in Pleiades and the associated connection types
"""

from airtight.cli import configure_commandline
import logging
from web import *

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
    ["-f", "--format", "ttl", "output format (supported values: ttl, csv)", False],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
]


def main(**kwargs):
    """
    main function
    """
    # logger = logging.getLogger(sys._getframe().f_code.co_name)
    if kwargs["format"] not in ["ttl", "csv"]:
        raise ValueError(f"Unsupported output format ({kwargs['format']})")
    j = get_json_dump()
    connections = list()
    for p in j["@graph"]:
        connections.extend(get_outbound_connections(None, p["uri"], p))
    if kwargs["format"] == "ttl":
        rows = [f"<{s}> <{p}> <{o}> ." for s, p, o in [c for c in connections]]
    elif kwargs["format"] == "csv":
        rows = [",".join(c) for c in connections]
    for r in rows:
        print(r)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
