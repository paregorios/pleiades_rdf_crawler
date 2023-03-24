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

from datetime import datetime, timedelta, timezone

import gzip
import json
import logging
from os.path import getmtime
from pathlib import Path
from pprint import pformat
from rdflib import Graph, Namespace, URIRef
import shutil
from webiquette.webi import Webi
from urllib.parse import urlparse
from validators import url as valid_uri

BASE_URI = "https://pleiades.stoa.org/places/"
CACHE_EXPIRATION = timedelta(hours=24)
logger = logging.getLogger(__name__)
ns_dcterms = Namespace("http://purl.org/dc/terms/")
ns_geo = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
BASE_URI_PLEIADES_RELATIONSHIP_TYPES = (
    "https://pleiades.stoa.org/vocabularies/relationship-types/"
)
ns_pleiades_relationship_types = Namespace(BASE_URI_PLEIADES_RELATIONSHIP_TYPES)
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


def get_json_dump() -> dict:
    ### get the entire JSON dump file from pleiades
    webi = get_web_interface("http://atlantides.org")
    uri = "http://atlantides.org/downloads/pleiades/json/pleiades-places-latest.json.gz"
    path = Path("data") / "all.json"
    fetch_json = False
    try:
        modified = datetime.fromtimestamp(getmtime(path), timezone.utc)
    except FileNotFoundError:
        fetch_json = True
    else:
        if modified.date() < datetime.today().date():
            fetch_json = True
    if fetch_json:
        logger.debug("Fetching fresh JSON")
        r = webi.get(uri, stream=True, bypass_cache=True)
        r.raw.decode_content = True
        gzip_file = gzip.GzipFile(fileobj=r.raw)
        with open(path, "wb") as f:
            shutil.copyfileobj(gzip_file, f)
    else:
        logger.debug("Local copy of json is less than a day old, so using that")
    with open(path, "r", encoding="utf-8") as f:
        j = json.load(f)
    del f
    return j


def get_place_graph(webi, puri, include_inbound=False) -> Graph:
    ### download and parse data about the place at puri and return it as an RDFLIB Graph
    ttl = get_ttl(webi, puri)
    g = Graph()
    g.parse(data=ttl, format="turtle")
    logger.debug(f"RDF for {puri} has {len(g)} triples.")

    # annoyingly, pleiades RDF doesn't have the connections from the database, so we have to build and add them from the JSON
    connections = get_outbound_connections(webi, puri)
    for c in connections:
        g.add(c)
    logger.debug(
        f"Modified RDF to add outbound connections from {puri} now has {len(g)} triples."
    )

    if include_inbound:
        connections = get_inbound_connections(webi, puri)
        for c in connections:
            g.add(c)
        logger.debug(
            f"Modified RDF to add inbound connections to {puri} now has {len(g)} triples."
        )

    return g


def get_outbound_connections(webi, puri, pdata: dict = None) -> list:
    ### get outbound connections from a puri and return a list of them as s, p, o tuples
    if pdata is None:
        j = get_json(webi, puri)
    else:
        j = pdata
    connections = j["connections"]
    logger.debug(f"JSON for {puri} has {len(connections)} connections.")
    triples = list()
    for c in connections:
        triples.append(
            (URIRef(puri), URIRef(c["connectionTypeURI"]), URIRef(c["connectsTo"]))
        )
    return triples


def get_inbound_connections(webi, puri):
    ### get inbound connections from a puri and return a list of them as s, p, o tuples
    j = get_json(webi, puri)
    inbound = j["connectsWith"]
    logger.debug(len(inbound))
    triples = list()
    for in_puri in inbound:
        triples.extend(
            [c for c in get_outbound_connections(webi, in_puri) if str(c[2]) == puri]
        )
    logger.debug(pformat(triples, indent=4))
    return triples


def get_repr_point(webi, puri) -> tuple:
    ### get the representative point for a puri from its json
    j = get_json(webi, puri)
    try:
        return tuple(j["reprPoint"])
    except TypeError:
        return None


def get_web_interface(uri=BASE_URI) -> Webi:
    ### instantiate and return a "webi" web interface object for the Pleiades website
    headers = {
        "User-Agent": "Pleiades4Sebs2023/0.1",
        "from": "pleiades.admin@nyu.edu",
    }
    return Webi(
        netloc=urlparse(uri).netloc, headers=headers, expire_after=CACHE_EXPIRATION
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
