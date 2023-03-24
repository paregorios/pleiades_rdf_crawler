#
# This module is part of the pleiades_rdf_crawler package
# https://github.com/paregorios/pleiades_rdf_crawler
#
# By Tom Elliott
# https://orcid.org/0000-0002-4114-66773
#
# Copyright 2023 New York University (non-faculty employee compensated work)
# GNU Affero General Public License (see LICENSE file)
#

"""
Web-related code for scripts in the pleiades_rdf_crawler
"""

from datetime import timedelta
import logging
from rdflib import Graph, URIRef
from webiquette.webi import Webi
from urllib.parse import urlparse
from validators import url as valid_uri

BASE_URI = "https://pleiades.stoa.org/places/"
CACHE_EXPIRATION = timedelta(hours=24)
logger = logging.getLogger(__name__)


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


def get_place_graph(webi, puri) -> Graph:
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
    return Webi(
        netloc=urlparse(BASE_URI).netloc, headers=headers, expire_after=CACHE_EXPIRATION
    )


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
