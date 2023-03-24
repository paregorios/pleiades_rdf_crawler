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
Find out what connections, if any, a particular Pleiades place has
"""

from airtight.cli import configure_commandline
import logging
from pprint import pformat, pprint
from rdflib import Graph, URIRef
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
    [
        "-b",
        "--bidi",
        False,
        "bidirectional, i.e. include inbound connections in addition to outbound",
        False,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["start_id", str, "Pleiades URI to start with"],
]


def main(**kwargs):
    """
    main function
    """
    vid = validate_id(kwargs["start_id"])
    webi = get_web_interface()
    p_graph = get_place_graph(webi, vid, include_inbound=kwargs["bidi"])
    ttl = p_graph.serialize(format="turtle")
    logger.debug(ttl)
    connections = list()
    logger.debug(f"\n\n{'-'*79}\n\n")
    for s, p, o in p_graph.triples((None, None, None)):
        assert isinstance(p, URIRef)
        if "route" in p:
            logger.debug(f"{s} {p} {o}")
        if p.startswith(BASE_URI_PLEIADES_RELATIONSHIP_TYPES):
            connections.append((s, p, o))
    c_count = len(connections)
    p_title = str(p_graph.value(URIRef(vid), ns_dcterms.title))
    print(
        f"P{vid.split('/')[-1]} {p_title} has {c_count} connection{('', 's')[c_count != 1]}:"
    )
    for c in connections:
        row = " ".join([f"<{item}>" for item in c])
        print(f"\t{row}")


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
