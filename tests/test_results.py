try:
    set
except NameError:
    from sets import Set as set
import unittest

import maps
import utils


class TestPrecinctsReportingPctFloat(unittest.TestCase):
    data_url = 'tests/data/20160301_super_tuesday.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_precincts_reporting_pct_less_than_one_point_oh(self):
        results = [r for r in self.candidate_reporting_units]
        for r in results:
            percent = float(r['precinctsreporting']) / float(r['precinctstotal'])
            self.assertEqual(
                "%.4f" % r['precinctsreportingpct'],
                "%.4f" % percent
            )
            self.assertLessEqual(r['precinctsreportingpct'], 1.00)
            self.assertGreaterEqual(r['precinctsreportingpct'], 0.00)


class TestMassRollupBug(unittest.TestCase):
    """
    Adding up all of the level "township" should equal
    the totals for "county" but that's not true for
    Nantucket county, MA and the townships in fips 25019.
    """
    data_url = 'tests/data/20160301_super_tuesday.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_number_of_counties(self):
        """
        According to bug #236, we should be 1 county short.
        """
        mass_results = [
            r for r in self.candidate_reporting_units if
            r['raceid'] == '24547' and
            r['level'] == 'county' and
            r['last'] == 'Trump'
        ]
        self.assertEqual(len(mass_results), len(maps.FIPS_TO_STATE['MA']))


class TestElectionDateSuperTuesday(unittest.TestCase):
    """
    When using data files, election date should be automatically inferred.
    """
    data_url = 'tests/data/20160301_super_tuesday.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_supertuesday_electiondate(self):
        self.assertEqual(self.electiondate, '2016-03-01')


class TestElectionDate2015(unittest.TestCase):
    """
    When using data files, election date should be automatically inferred.
    """
    data_url = 'tests/data/20151103_national.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_2015_electiondate(self):
        self.assertEqual(self.electiondate, '2015-11-03')


class TestGeneralElectionEdgeCases(unittest.TestCase):
    """
    There should be 51 unique state reportingunit ids, not 1.
    """
    data_url = 'tests/data/20121106_national.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_general_stateids(self):
        state_results = [r['reportingunitid'] for r in self.candidate_reporting_units if r['level'] == 'state']
        unique_state_results = list(set(state_results))
        self.assertEqual(len(unique_state_results), 51)
