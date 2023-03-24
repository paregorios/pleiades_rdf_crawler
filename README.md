# pleiades_rdf_crawler

Experiments in collecting, parsing, and reusing connections in the Pleiades gazetteer of ancient places. 

By: Tom Elliott, ISAW/NYU
https://orcid.org/0000-0002-4114-6677

Copyright 2023 New York University (non-faculty employee compensated work)
GNU Affero General Public License (see LICENSE file)

## Install

I'm running this under Python 3.11.2 installed under MacOS Monterey in a virtual environment setup and managed with [direnv](https://direnv.net/) and [pyenv](https://github.com/pyenv/pyenv) (both installed via [homebrew](https://brew.sh/)). Here's my setup:

- make sure `pyenv` has the version of python we want in its local arsenal: `pyenv install 3.11.2`
- clone repos from github into a clean local directory
- cd into the local clone
- `echo "layout pyenv 3.11.2" > .envrc`
- `direnv allow`
- `which python` should show `$PWD/.direnv/python-3.11.2/bin/python`
- `pip install -U pip`
- `pip install -r requirements.txt` (see further "dependencies" below)

## Availabile scripts

### got_conns.py

List all the connections involving a particular place.

```
python got_conns.py -h
usage: got_conns.py [-h] [-l LOGLEVEL] [-v] [-w] [-b] start_id

Find out what connections, if any, a particular Pleiades place has

positional arguments:
  start_id              Pleiades URI to start with

options:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --loglevel LOGLEVEL
                        desired logging level (case-insensitive string: DEBUG, INFO,
                        WARNING, or ERROR) (default: NOTSET)
  -v, --verbose         verbose output (logging level == INFO) (default: False)
  -w, --veryverbose     very verbose output (logging level == DEBUG) (default: False)
  -b, --bidi            bidirectional, i.e. include inbound connections in addition to
                        outbound (default: False)
```

By default, the script only returns outbound connections (i.e., where the specified Pleiades ID is the subject of a connection triple).

```
P579885 Athenae has 1 connection:
	<https://pleiades.stoa.org/places/579885> <https://pleiades.stoa.org/vocabularies/relationship-types/capital> <https://pleiades.stoa.org/places/579888>
```

The `-b` (`--bidi`) option searches also for connections inbound to the specified Pleiades ID (i.e., where it is the object of a connection triple).

```
python got_conns.py -b 579885
P579885 Athenae has 33 connections:
	<https://pleiades.stoa.org/places/585959> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_physical> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/580062> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_admin> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/468194251> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/277534797> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/649966335> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/580051> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/585128> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/750203268> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/491444298> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/579885> <https://pleiades.stoa.org/vocabularies/relationship-types/capital> <https://pleiades.stoa.org/places/579888>
	<https://pleiades.stoa.org/places/580123> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/759679649> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/992770796> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/310115518> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/773761100> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/728329644> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/122572945> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/649966334> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/638356144> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/954340915> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/558659669> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/720198157> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/650003009> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/968858713> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_physical> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/146086514> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/969121823> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_physical> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/807514119> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/235795850> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/97294452> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/659771158> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_physical> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/935764097> <https://pleiades.stoa.org/vocabularies/relationship-types/at> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/813654446> <https://pleiades.stoa.org/vocabularies/relationship-types/connection> <https://pleiades.stoa.org/places/579885>
	<https://pleiades.stoa.org/places/168254096> <https://pleiades.stoa.org/vocabularies/relationship-types/part_of_regional> <https://pleiades.stoa.org/places/579885>
```

### conn2lines.py

Attempt to construct spatial lines for export to GeoJSON from designated typed connections in Pleiades data. Invoke the script with a list of [connection types](https://pleiades.stoa.org/vocabularies/relationship-types) to follow, and a Pleiades place URI at which to start. Then it crawls the Pleiades read API to get the relevant data, which it parses to construct and output the lines. It's generally useful to run it in "verbose" mode (-v) in order to see what's happening. Very-verbose mode (-w) will get you a wall of debugging output if you're into that sort of thing.

```
python conn2lines.py -h
usage: conn2lines.py [-h] [-l LOGLEVEL] [-v] [-w] -c CONNTYPES start_id

Crawl graphs of typed Pleiades connections and build straight lines between them in
GeoJSON

positional arguments:
  start_id              Pleiades URI to start with

options:
  -h, --help            show this help message and exit
  -l LOGLEVEL, --loglevel LOGLEVEL
                        desired logging level (case-insensitive string: DEBUG, INFO,
                        WARNING, or ERROR (default: NOTSET)
  -v, --verbose         verbose output (logging level == INFO) (default: False)
  -w, --veryverbose     very verbose output (logging level == DEBUG) (default: False)
  -c CONNTYPES, --conntypes CONNTYPES
                        comma-separate list of Pleiades relationship type terms that you
                        want to follow (default: )
```

Here's an example that collects and constructs lines for ancient routes (e.g., Peutinger Map, Antontine Itinerary) recorded with connections in Pleiades, beginning at [ancient Tipasa (modern Tipaza on the Mediterranean coast of Algeria)](https://pleiades.stoa.org/places/295363):

```
python conn2lines.py -v -c route_next https://pleiades.stoa.org/places/295363
INFO:root:logging level changed to INFO via command line option; was WARNING
INFO:__main__:found 20 connected places by crawling connections of type(s) ['route_next'] beginning at place https://pleiades.stoa.org/places/295363 (Tipasa)
INFO:__main__:connected places:
{   'https://pleiades.stoa.org/places/295228': 'Bida',
    'https://pleiades.stoa.org/places/295243': 'Casae Calventi?',
    'https://pleiades.stoa.org/places/295253': 'Cissi',
    'https://pleiades.stoa.org/places/295276': 'Icosium',
    'https://pleiades.stoa.org/places/295280': 'Iomnium',
    'https://pleiades.stoa.org/places/295331': 'Rusguniae',
    'https://pleiades.stoa.org/places/295332': 'Rusippisir',
    'https://pleiades.stoa.org/places/295333': 'Rusubbicari Matidiae',
    'https://pleiades.stoa.org/places/295334': 'Rusuccuru',
    'https://pleiades.stoa.org/places/295359': 'Tigisi',
    'https://pleiades.stoa.org/places/295363': 'Tipasa',
    'https://pleiades.stoa.org/places/305062': 'Choba',
    'https://pleiades.stoa.org/places/305063': 'Chullu',
    'https://pleiades.stoa.org/places/305095': 'Igilgili',
    'https://pleiades.stoa.org/places/305111': 'Muslubium',
    'https://pleiades.stoa.org/places/305126': 'Paccianis Matidiae?/Tucca?',
    'https://pleiades.stoa.org/places/305137': 'Rusicade/Thapsus',
    'https://pleiades.stoa.org/places/305138': 'Rusazus?',
    'https://pleiades.stoa.org/places/305142': 'Saldae',
    'https://pleiades.stoa.org/places/835084119': 'Ruzai'}
INFO:__main__:found coordinates for 20 of 20 connected places in our graph
INFO:__main__:coordinates:
{   'https://pleiades.stoa.org/places/295228': (4.285625, 36.682160499999995),
    'https://pleiades.stoa.org/places/295243': (2.68789, 36.641597),
    'https://pleiades.stoa.org/places/295253': (3.7334035, 36.877461),
    'https://pleiades.stoa.org/places/295276': (3.0532175, 36.7689125),
    'https://pleiades.stoa.org/places/295280': (4.1232690000000005, 36.893024),
    'https://pleiades.stoa.org/places/295331': (3.2378935, 36.799094499999995),
    'https://pleiades.stoa.org/places/295332': (4.156907, 36.897601),
    'https://pleiades.stoa.org/places/295333': (3.5646, 36.801017),
    'https://pleiades.stoa.org/places/295334': (   3.9096444999999997,
                                                   36.912854499999995),
    'https://pleiades.stoa.org/places/295359': (3.947273, 36.793307),
    'https://pleiades.stoa.org/places/295363': (2.44286185004, 36.5946473891),
    'https://pleiades.stoa.org/places/305062': (5.4607425, 36.6665775),
    'https://pleiades.stoa.org/places/305063': (6.562081, 37.0078525),
    'https://pleiades.stoa.org/places/305095': (5.766168, 36.8212995),
    'https://pleiades.stoa.org/places/305111': (5.246097, 36.636739),
    'https://pleiades.stoa.org/places/305126': (6.1015385, 36.865147),
    'https://pleiades.stoa.org/places/305137': (6.9055805, 36.8814425),
    'https://pleiades.stoa.org/places/305138': (4.420813, 36.894041),
    'https://pleiades.stoa.org/places/305142': (5.057964999999999, 36.740851),
    'https://pleiades.stoa.org/places/835084119': None}
```

**To do**: actually write the geojson

## Dependencies

All dependencies are in `requirements.txt`. Here's what and why for each:

### airtight

Available via pypi, this is a package I wrote a while back to make the setup of arguments and logging the way I often use it in scripts easier. 

### rdflib

Well, we're working with RDF here so...

### validators

I hate trying to write regexes for URLs.

### webiquette

This one's pulled from github because both python packaging and pypi release procedures have changed yet again and I haven't had a chance to learn how to comply with the new regimes, but we do need the latest features of the package.

This is another package I wrote, and its aim is to make us easily well-behaved (and fast!) with all these web requests we're issuing. Specifically, the package wraps `requests` and `requests_cache` so we get simple, robust handling of the HTTP requests we issue, and caching of the responses locally (in `./data/cache`, which it creates if necessary) so re-runs are super-fast and don't generate repeated HTTP requests for unchanged data on the server. It also makes it easy for us to specify a user agent in our HTTP request headers, and it automatically complies with the target server's robots.txt file (allow, disallow, and crawl delay). It also performs backoff-delayed retries when it encounters `ConnectionError` or `RemoteDisconnected`. There is plenty of flexibility around parameters for all this behavior, but we're just running with the defaults, except for: 

- setting a custom [user agent string](https://en.wikipedia.org/wiki/User_agent), which everyone everywhere should always do in every script they write
- setting the local cache expiration to 24 hours instead of the default 30 days, in case something changes on the server

Note: the easiest way to ignore local caching completely for your next run of the script is to blow away the cache files locally: `rm -rf data/cache`, but note that this does nothing about bypassing server-side caching.
