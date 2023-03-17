"""
Crawl graphs of typed Pleiades connections and build straight lines between them in GeoJSON
"""

from airtight.cli import configure_commandline
import logging
from pprint import pformat, pprint
from rdflib import Graph, Namespace, URIRef
from urllib.parse import urlparse
from validators import url as valid_uri
from webiquette.webi import Webi

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
BASE_URI = "https://pleiades.stoa.org/places/"
ns_dcterms = Namespace("http://purl.org/dc/terms/")
ns_geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
ns_pleiades_relationship_types = Namespace(
    "https://pleiades.stoa.org/vocabularies/relationship-types/"
)
ns_pleiades_places = Namespace("https://pleiades.stoa.org/places/vocab#")


def get_ttl(webi, puri) -> str:
    ### download and return RDF/TTL for puri as text
    r = webi.get(puri + "/turtle")
    if r.status_code != 200:
        r.raise_for_status()
    return r.text


def get_json(webi, puri) -> dict:
    ### download and return JSON for puri as a python dict
    r = webi.get(puri + "/json")
    if r.status_code != 200:
        r.raise_for_status()
    return r.json()


def get_place(webi, puri) -> Graph:
    ### download and parse data about the place at puri and return it as an RDFLIB Graph
    ttl = get_ttl(webi, puri)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    logger.debug(f"RDF for {puri} has {len(g)} triples.")

    # annoyingly, pleiades RDF doesn't have the connections from the database, so we have to build and add them from the JSON
    j = get_json(webi, puri)
    connections = j["connections"]
    logger.debug(f"JSON for {puri} has {len(connections)} connections.")
    for c in connections:
        g.add((URIRef(puri), URIRef(c["connectionTypeURI"]), URIRef(c["connectsTo"])))
    logger.debug(f"Modified RDF for {puri} now has {len(g)} triples.")
    return g


def get_repr_point(webi, puri) -> tuple:
    ### get the representative point for a puri from its json
    j = get_json(webi, puri)
    try:
        return tuple(j["reprPoint"])
    except TypeError:
        return None


def get_web_interface() -> Webi:
    ### instantiate and return a "webi" web interface object for the Pleiades website
    headers = {
        "User-Agent": "Pleiades4Sebs2023/0.1",
        "from": "pleiades.admin@nyu.edu",
    }
    return Webi(netloc=urlparse(BASE_URI).netloc, headers=headers)


def raise_invalid_uri(v):
    ### raise a value error for an invalid Pleiades URI
    raise ValueError(f"Invalid Pleiades URI or ID: {v}")


def validate_id(v):
    ### validate and coerce if necessary a Pleiades place ID or URI
    id = v
    while True:
        if not (valid_uri(id)):
            try:
                int(id)
            except ValueError:
                raise_invalid_uri(v)
            else:
                id = BASE_URI + id
        elif not id.startswith(BASE_URI):
            raise_invalid_uri(v)
        else:
            return id


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
            connected_places[puri] = get_place(webi, puri)
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
