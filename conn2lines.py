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
Crawl graphs of typed Pleiades connections and build straight lines between them in GeoJSON
"""

from airtight.cli import configure_commandline
import logging
from pprint import pformat, pprint
from rdflib import Graph, Namespace, URIRef
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
        "-c",
        "--conntypes",
        "",
        "comma-separate list of Pleiades relationship type terms that you want to follow",
        True,
    ],
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["start_id", str, "Pleiades URI to start with"],
]
ns_dcterms = Namespace("http://purl.org/dc/terms/")
ns_geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
ns_pleiades_relationship_types = Namespace(
    "https://pleiades.stoa.org/vocabularies/relationship-types/"
)
ns_pleiades_places = Namespace("https://pleiades.stoa.org/places/vocab#")


def main(**kwargs):
    """
    main function
    """
    conntype_terms = kwargs["conntypes"].split(",")
    conntypes = [
        getattr(ns_pleiades_relationship_types, ct.strip()) for ct in conntype_terms
    ]
    vid = validate_id(kwargs["start_id"])
    connected_places = {vid: None}
    webi = get_web_interface()

    # crawl connections and load connected places until we run out of paths
    while True:
        puris_to_parse = {puri for puri, g in connected_places.items() if g is None}
        if not puris_to_parse:
            break
        for puri in puris_to_parse:
            connected_places[puri] = get_place_graph(webi, puri)
            for contype in conntypes:
                for s, p, o in connected_places[puri].triples((None, contype, None)):
                    try:
                        connected_places[str(o)]
                    except KeyError:
                        connected_places[str(o)] = None

    # get titles for each connected place so we can provide more human-readable output
    place_titles = {
        puri: str(g.value(URIRef(puri), ns_dcterms.title))
        for puri, g in connected_places.items()
    }

    logger.info(
        f"found {len(connected_places)} connected places by crawling connections of type(s) {conntype_terms} beginning at place {vid} ({place_titles[vid]})"
    )
    logger.info(f"connected places:\n{pformat(place_titles, indent=4)}")

    # get the union of all the individual place graphs
    big_graph = Graph()
    for puri, g in connected_places.items():
        big_graph += g
    logger.debug(f"There are {len(big_graph)} triples in big_graph")
    for contype in conntypes:
        for s, p, o in big_graph.triples((None, contype, None)):
            logger.debug(f"<{s}> <{p}> <{o}>")

    # get coordinates for all the places in the connections of interest
    coords = dict()
    for puri in connected_places.keys():
        s = URIRef(puri)
        try:
            coords[puri] = (
                # note coordinate order is x, y (long, lat) a la geojson
                float(big_graph.value(s, ns_geo.long)),
                float(big_graph.value(s, ns_geo.lat)),
            )
        except TypeError:
            # annoyingly, Pleiades RDF only includes representative point coordinates for places with a
            # single location that has point geometry, so for the more complex cases we have to get the
            # representative point from the Pleiades JSON
            coords[puri] = get_repr_point(webi, puri)
    logger.info(
        f"found coordinates for {len(coords)} of {len(connected_places)} connected places in our graph"
    )
    logger.info(f"coordinates:\n{pformat(coords, indent=4)}")

    # create a line from subject to object for each connection and save to csv
    conn_lines = list()
    for contype in conntypes:
        for s, p, o in big_graph.triples((None, contype, None)):
            s_uri = str(s)
            p_uri = str(p)
            o_uri = str(o)
            conn_lines.append((s_uri, p_uri, o_uri, [coords[s_uri], coords[o_uri]]))
    logger.debug(f"connection lines:\n{pformat(conn_lines, indent=4)}")


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
