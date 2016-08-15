import csv
from collections import namedtuple
import sys
from sets import Set

import ujson


candidate_rerporting_unit_template = {
    u'incumbent': None,
    u'electiondate': None,
    u'candidateid': None,
    u'raceid': None,
    u'precinctsreporting': None,
    u'officeid': None,
    u'ballotorder': None,
    u'fipscode': None,
    u'reportingunitname': None,
    u'winner': None,
    u'lastupdated': None,
    u'polid': None,
    u'test': None,
    u'party': None,
    u'racetypeid': None,
    u'description': None,
    u'precinctsreportingpct': None,
    u'polnum': None,
    u'level': None,
    u'reportingunitid': None,
    u'precinctstotal': None,
    u'last': None,
    u'statepostal': None,
    u'racetype': None,
    u'officename': None,
    u'votecount': None,
    u'seatname': None,
    u'votepct': 0.0
}


def output_json(payload):
    """
    Generically dumps to JSON.
    """
    sys.stdout.write(ujson.dumps(payload))


def output_csv(payload):
    """
    Generically dumps to a CSV on stdout.
    """
    payload_keys = []
    for p in payload:
        for k in p.keys():
            payload_keys.append(k)

    writer = csv.DictWriter(sys.stdout, fieldnames=list(Set(payload_keys)))
    writer.writeheader()

    for p in payload:
        writer.writerow(p)


def open_file(file_path, race_ids=None):
    """
    Opens and returns an AP JSON file.
    """
    with open(file_path, 'r') as readfile:
        parsed_json = ujson.loads(readfile.read())
        electiondate = parsed_json['electionDate']
        if race_ids:
            return (electiondate, [r for r in parsed_json['races'] if r in race_ids])
        else:
            return (electiondate, parsed_json['races'])


def load_races(races):
    """
    Given a list of AP JSON races, returns only those races.
    """
    payload = []
    for r in races:
        if r.get('reportingUnits', None):
            del r['reportingUnits']
        if r.get('candidates', None):
            del r['candidates']

        r = {k.lower(): v for k, v in r.items()}
        payload.append(r)

    return payload


def load_candidates(races):
    """
    Given a list of AP JSON races, returns unique candidates from them.
    """
    candidates = []

    for r in races:
        if r.get('reportingUnits', None):
            for ru in r['reportingUnits']:
                for c in ru['candidates']:
                    # Lowercases the keys with a dict comprehension.
                    candidates.append({k.lower(): v for k, v in c.items()})

    # Loops over candidates, transforms the dicts into tuples, sorts by key, adds to a set for
    # uniqueness, then transforms that set into a list.
    unique_candidates = list(Set([tuple(sorted(c.items(), key=lambda x: x[0])) for c in candidates]))

    # Turns all the tuples in that list back into dicts.
    return [dict(k) for k in unique_candidates]


def load_reportingunits(races):
    """
    Given a list of AP JSON races, reuturns reportingunit objects.
    """
    payload = []

    for r in races:
        if r.get('reportingUnits', None):
            for ru in r['reportingUnits']:
                for k, v in r.items():
                    if k != 'reportingUnits':
                        ru[k] = v
                ru = {k.lower(): v for k, v in ru.items()}
                payload.append(ru)

    return payload


def load_results(electiondate, races):
    """
    Given a list of AP JSON races, returns candidate-reportingunit-race
    objects, e.g., results.
    """

    payload = []

    for r in races:
        if r.get('reportingUnits', None):
            for ru in r['reportingUnits']:
                for c in ru['candidates']:
                    cru = candidate_rerporting_unit_template.copy()

                    # Add reporting unit data to the candidate.
                    for k, v in ru.items():
                        if k != 'candidates':
                            c[k] = v

                    # Add race data to the candidate.
                    for k, v in r.items():
                        if k != 'reportingUnits':
                            c[k] = v

                    c = {k.lower(): v for k, v in c.items()}

                    if c['level'] == 'state':
                        c['reportingunitid'] = c['statepostal']

                    c['electiondate'] = electiondate

                    cru.update(c)

                    # The result is a single dict for each candidate-reportingunit-race.
                    payload.append(cru)

    return payload
