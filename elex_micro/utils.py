import csv
from collections import namedtuple, defaultdict, OrderedDict
import sys
from sets import Set

import ujson

import maps

CRU_TEMPLATE = OrderedDict((
    (u'id', None),
    (u'raceid', None),
    (u'racetype', None),
    (u'racetypeid', None),
    (u'ballotorder', None),
    (u'candidateid', None),
    (u'description', None),
    (u'delegatecount', None),
    (u'electiondate', None),
    (u'fipscode', None),
    (u'first', None),
    (u'incumbent', False),
    (u'initialization_data', False),
    (u'is_ballot_measure', False),
    (u'last', None),
    (u'lastupdated', None),
    (u'level', None),
    (u'national', False),
    (u'officeid', None),
    (u'officename', None),
    (u'party', None),
    (u'polid', None),
    (u'polnum', None),
    (u'precinctsreporting', None),
    (u'precinctsreportingpct', None),
    (u'precinctstotal', None),
    (u'reportingunitid', None),
    (u'reportingunitname', None),
    (u'runoff', None),
    (u'seatname', None),
    (u'seatnum', None),
    (u'statename', None),
    (u'statepostal', None),
    (u'test', False),
    (u'totalvotes', 0),
    (u'uncontested', False),
    (u'votecount', 0),
    (u'votepct', 0.0),
    (u'winner', False),
))

# CRU_TEMPLATE = OrderedDict(
#     (u'incumbent', False),
#     (u'electiondate', None),
#     (u'candidateid', None),
#     (u'raceid', None),
#     (u'precinctsreporting', None),
#     (u'officeid', None),
#     (u'ballotorder', None),
#     (u'fipscode', None),
#     (u'reportingunitname', None),
#     (u'winner', None),
#     (u'lastupdated', None),
#     (u'polid', None),
#     (u'test', None),
#     (u'party', None),
#     (u'racetypeid', None),
#     (u'description', None),
#     (u'precinctsreportingpct', None),
#     (u'polnum', None),
#     (u'level', None),
#     (u'reportingunitid', None),
#     (u'precinctstotal', None),
#     (u'last', None),
#     (u'statepostal', None),
#     (u'racetype', None),
#     (u'officename', None),
#     (u'votecount', None),
#     (u'seatname', None),
#     (u'totalvotes', None),
#     (u'votepct', 0.0),
# )

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


def calculate_pcts(races, votecounts):
    """
    Given a dictionary of raceids with their nested reportingunits to get
    vote totals for that reporting unit in this shape:
    {
        "18525": {
            "county-18038": 1104
        }
    }

    Will decorate each candidate-reporting-unit with the total votes and
    the vote percentage.
    """
    for r in races:
        r['totalvotes'] = votecounts[r['raceid']][r['reportingunitid']]
        try:
            r['votepct'] = float(r['votecount']) / float(r['totalvotes'])
        except ZeroDivisionError:
            pass
    return races


def load_results(electiondate, races):
    """
    Given a list of AP JSON races, returns candidate-reportingunit-race
    objects, e.g., results.
    """

    payload = []
    votecounts = {}

    for r in races:
        if r.get('reportingUnits', None):

            # Create data structure for aggregating votes.
            if not votecounts.get(r['raceID'], None):
                votecounts[r['raceID']] = {}

            for ru in r['reportingUnits']:
                for c in ru['candidates']:
                    cru = CRU_TEMPLATE.copy()

                    # Add reporting unit data to the candidate.
                    for k, v in ru.items():
                        if k not in ['candidates', 'votecount']:
                            c[k] = v

                    # Add race data to the candidate.
                    for k, v in r.items():
                        if k != 'reportingUnits':
                            c[k] = v

                    # Lowercase the keys.
                    c = {k.lower(): v for k, v in c.items()}

                    if c.get('fipscode', None):
                        c['fipscode'] = c['fipscode'].zfill(5)

                    if c['level'] == 'subunit':
                        c['level'] = 'county'

                    if c['statepostal'] in maps.FIPS_TO_STATE.keys():
                        if c['level'] == 'subunit':
                            c['level'] = 'township'

                    # Set the reportingunitid.
                    if c['level'] == 'state':
                        c['reportingunitid'] = 'state-1'
                    else:
                        c['reportingunitid'] = "%s-%s" % (c['level'], c['reportingunitid'])

                    # Set the unique id.
                    if c.get('polid', None):
                        c['id'] = "%s-polid-%s-%s" % (c['raceid'], c['polid'], c['reportingunitid'])
                    else:
                        c['id'] = "%s-polnum-%s-%s" % (c['raceid'], c['polnum'], c['reportingunitid'])

                    # Aggregate vote counts for this reportingunit.
                    if not votecounts[r['raceID']].get(c['reportingunitid'], None):
                        votecounts[r['raceID']][c['reportingunitid']] = c['votecount']
                    else:
                        votecounts[r['raceID']][c['reportingunitid']] += c['votecount']

                    c['electiondate'] = electiondate

                    if c.get('winner', None):
                        if c['winner'].lower().strip() == 'x':
                            c['winner'] = True

                    # Update the dict template we have with real data.
                    # This makes sure every key has at least the default values.
                    cru.update(c)

                    # The result is a single dict for each candidate-reportingunit-race.
                    payload.append(cru)


    return payload,votecounts
