import csv
import sys
from sets import Set

import ujson


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


def load_results(races):
    """
    Given a list of AP JSON races, returns candidate-reportingunit-race
    objects, e.g., results.
    """
    payload = []

    for r in races:
        if r.get('reportingUnits', None):
            for ru in r['reportingUnits']:
                for c in ru['candidates']:

                    # Add reporting unit data to the candidate.
                    for k, v in ru.items():
                        if k != 'candidates':
                            c[k] = v

                    # Add race data to the candidate.
                    for k, v in r.items():
                        if k != 'reportingUnits':
                            c[k] = v

                    c = {k.lower(): v for k, v in c.items()}

                    # The result is a single dict for each candidate-reportingunit-race.
                    payload.append(c)

    return payload
