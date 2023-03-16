"""
play1
"""

from airtight.cli import configure_commandline
import logging
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
]
POSITIONAL_ARGUMENTS = [
    # each row is a list with 3 elements: name, type, help
    ["start_id", str, "Pleiades URI to start with"]
]
BASE_URI = "https://pleiades.stoa.org/places/"
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
    start_uri = validate_id(kwargs["start_id"])
    logger.debug(f"start_uri: {start_uri}")

    webi = get_web_interface()

    pg = get_place(webi, start_uri)


if __name__ == "__main__":
    main(
        **configure_commandline(
            OPTIONAL_ARGUMENTS, POSITIONAL_ARGUMENTS, DEFAULT_LOG_LEVEL
        )
    )
