import csv
import sys

import ujson

import maps

KEY_ORDER = (
    'id',
    'raceid',
    'racetype',
    'racetypeid',
    'abbrv',
    'ballotorder',
    'candidateid',
    'description',
    'delegatecount',
    'electiondate',
    'electtotal',
    'electwon',
    'fipscode',
    'first',
    'incumbent',
    'initialization_data',
    'is_ballot_measure',
    'last',
    'lastupdated',
    'level',
    'middle',
    'national',
    'numrunoff',
    'numwinners',
    'officeid',
    'officename',
    'party',
    'polid',
    'polnum',
    'precinctsreporting',
    'precinctsreportingpct',
    'precinctstotal',
    'reportingunitid',
    'reportingunitname',
    'runoff',
    'seatname',
    'seatnum',
    'statename',
    'statepostal',
    'suffix',
    'test',
    'totalvotes',
    'uncontested',
    'votecount',
    'votepct',
    'winner'
)


def output_json(payload):
    """
    Generically dumps to JSON.
    """
    sys.stdout.write(ujson.dumps(payload))


def output_csv(payload):
    """
    Generically dumps to a CSV on stdout.
    """
    writer = csv.DictWriter(sys.stdout, fieldnames=KEY_ORDER)
    writer.writeheader()

    for p in payload:
        writer.writerow(p)


def output_tsv(payload):
    sys.stdout.write("\t".join(payload[0].keys()))
    for p in payload:
        sys.stdout.write("\t".join(p.values()))


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


def lowercase_keys(c):
    c = {k.lower(): v for k, v in c.items()}
    return c


def pad_fips(c):
    if c.get('fipscode', None):
        c['fipscode'] = c['fipscode'].zfill(5)
    return c


def set_statename(c):
    if c['statepostal']:
        c['statename'] = maps.STATE_ABBR[c['statepostal']]
    return c


def set_county(c):
    if c['statepostal'] in maps.FIPS_TO_STATE.keys():
        if c['level'] == 'subunit':
            c['level'] = 'township'
    elif c['level'] == 'subunit':
        c['level'] = 'county'
    return c


def set_reportingunitname(c):
    try:
        if not c['reportingunitname']:
            c['reportingunitname'] = ''
    except KeyError:
        c['reportingunitname'] = ''
    return c


def set_township(c):
    try:
        if c['statepostal'] in maps.FIPS_TO_STATE.keys():
            if c['level'] == 'subunit':
                c['level'] = 'township'
    except KeyError:
        pass
    return c


def set_reportingunitid(c):
    # Set the reportingunitid.
    if c['level'] == 'state':
        c['reportingunitid'] = '%s-1' % c['statepostal']
    elif c['level'] == 'national':
        c['reportingunitid'] = 'national-0'
    else:
        c['reportingunitid'] = "%s-%s" % (c['level'], c['reportingunitid'])
    return c


def set_uniqueid(c):
    # Set the unique id.
    if c.get('polid', None):
        c['id'] = "%s-polid-%s-%s" % (c['raceid'], c['polid'], c['reportingunitid'])
    else:
        c['id'] = "%s-polnum-%s-%s" % (c['raceid'], c['polnum'], c['reportingunitid'])
    return c


def set_winner(c):
    if c.get('winner', None):
        if c['winner'].lower().strip() == 'x':
            c['winner'] = True
    return c


def set_electiondate(c, electiondate):
    c['electiondate'] = electiondate
    return c


def aggregate_votecounts(votecounts, c, r):
    # Aggregate vote counts for this reportingunit.
    if not votecounts[r['raceID']].get(c['reportingunitid'], None):
        votecounts[r['raceID']][c['reportingunitid']] = c['votecount']
    else:
        votecounts[r['raceID']][c['reportingunitid']] += c['votecount']
    return votecounts


def compute_pcts(payload, votecounts):
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
    for r in payload:
        r['totalvotes'] = votecounts[r['raceid']][r['reportingunitid']]
        try:
            r['votepct'] = float(r['votecount']) / float(r['totalvotes'])
        except ZeroDivisionError:
            pass
    return payload


    def set_new_england_counties(r):
        if r['statepostal'] in maps.FIPS_TO_STATE.keys():

            counties = {}

            for c in maps.FIPS_TO_STATE[r['statepostal']].keys():
                try:
                    counties[c] = dict([
                        r.__dict__ for
                        r in r['reportingunits'] if
                        r.level == 'township' and
                        "Mail Ballots C.D." not in r.reportingunitname and
                        r.fipscode == c
                    ][0])

                    # Set some basic information we know about the county.
                    counties[c]['level'] = 'county'
                    counties[c]['statepostal'] = r['statepostal']
                    counties[c]['candidates'] = {}
                    counties[c]['reportingunitname'] =\
                        maps.FIPS_TO_STATE[r['statepostal']][c]
                    counties[c]['reportingunitid'] = "%s-%s" % (
                        r['statepostal'],
                        c
                    )

                    reporting_units = [
                        r for
                        r in r['reportingunits'] if
                        r.level == 'township' and
                        "Mail Ballots C.D." not in r.reportingunitname and
                        r.fipscode == c
                    ]

                    # Declaratively sum the precincts / votes for this county.
                    counties[c]['precinctstotal'] = sum([
                        r.precinctstotal for
                        r in reporting_units if
                        r.level == 'township' and
                        "Mail Ballots C.D." not in r.reportingunitname and
                        r.fipscode == c
                    ])
                    counties[c]['precinctsreporting'] = sum([
                        r.precinctsreporting for
                        r in reporting_units if
                        r.level == 'township' and
                        "Mail Ballots C.D." not in r.reportingunitname and
                        r.fipscode == c
                    ])

                    pcts_tot = float(counties[c]['precinctstotal'])
                    pcts_rep = float(counties[c]['precinctsreporting'])

                    try:
                        counties[c]['precinctsreportingpct'] = pcts_rep / pcts_tot
                    except ZeroDivisionError:
                        counties[c]['precinctsreportingpct'] = 0.0

                    counties[c]['votecount'] = sum([
                        int(r.votecount or 0) for
                        r in reporting_units if
                        r.level == 'township' and
                        "Mail Ballots C.D." not in r.reportingunitname and
                        r.fipscode == c
                    ])

                    for r in reporting_units:

                        # Set up candidates for each county.
                        for cru in r.candidates:
                            if not counties[c]['candidates'].get(cru.unique_id, None):
                                d = dict(cru.__dict__)
                                d['level'] = 'county'
                                d['reportingunitid'] = "%s-%s" % (
                                    r['statepostal'],
                                    c
                                )
                                fips_dict = maps.FIPS_TO_STATE[r['statepostal']]
                                d['reportingunitname'] = fips_dict[c]
                                counties[c]['candidates'][cru.unique_id] = d

                            else:
                                d = counties[c]['candidates'][cru.unique_id]
                                d['votecount'] += cru.votecount
                                d['precinctstotal'] += cru.precinctstotal
                                d['precinctsreporting'] += cru.precinctsreporting

                                try:
                                    d['precinctsreportingpct'] = (
                                        float(d['precinctsreporting']) /
                                        float(d['precinctstotal'])
                                    )

                                except ZeroDivisionError:
                                    d['precinctsreportingpct'] = 0.0

                except IndexError:
                    """
                    This is the ME bug from the ME primary.
                    """
                    pass

            try:
                for ru in counties.values():
                    ru['candidates'] = ru['candidates'].values()
                    ru['statename'] = str(maps.STATE_ABBR[ru['statepostal']])
                    r = ReportingUnit(**ru)
                    r['reportingunits'].append(r)

            except AttributeError:
                """
                Sometimes, the dict is empty because we have no townships to
                roll up into counties. Issue #228.
                """
                pass


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

                    # Create a default dictionary out of our KEY_ORDER
                    # tuple where the default value is None.
                    cru = dict(((k, None) for k in KEY_ORDER))

                    # Add reporting unit data to the candidate.
                    for k, v in ru.items():
                        if k not in ['candidates', 'votecount']:
                            if k == 'precinctsReportingPct':
                                v = float(v) / 100
                            c[k] = v

                    # Add race data to the candidate.
                    for k, v in r.items():
                        if k != 'reportingUnits':
                            c[k] = v

                    # Transform the results.
                    c = lowercase_keys(c)
                    c = set_electiondate(c, electiondate)
                    c = set_winner(c)
                    c = set_county(c)
                    c = set_statename(c)
                    c = set_township(c)
                    c = pad_fips(c)
                    c = set_reportingunitid(c)
                    c = set_reportingunitname(c)
                    c = set_uniqueid(c)

                    # Get vote totals for each reportingunit.
                    votecounts = aggregate_votecounts(votecounts, c, r)

                    # Update the dict template we have with real data.
                    # This makes sure every key has at least the default values.
                    cru.update(c)

                    # The result is a single dict for each candidate-reportingunit-race.
                    payload.append(cru)

    # When returning, annotate each reportingunit with vote totals and pcts.
    return compute_pcts(payload, votecounts)
