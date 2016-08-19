import unittest

import utils


class TestCandidateReportingUnit(unittest.TestCase):
    file_path = 'tests/data/20151103_national.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.file_path)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_cru_has_keys(self):
        c = self.candidate_reporting_units[0]
        self.assertTrue(c.get('reportingunitid', None))

    def test_zero_votes(self):
        cru = [
            c for c in self.candidate_reporting_units
            if c['reportingunitid'] == '6020'
        ]

        for c in cru:
            self.assertEqual(c['votepct'] + c['votecount'], 0.0)

    def test_number_of_parsed_candidate_reporting_units(self):
        self.assertEqual(len(self.candidate_reporting_units), 505)

    def test_existence_of_electiondate(self):
        cru = self.candidate_reporting_units[0]
        self.assertTrue(cru.get('electiondate', None))

    def test_correct_electiondate(self):
        cru = self.candidate_reporting_units[0]
        self.assertEqual('2015-11-03', cru['electiondate'])

    def test_candidate_reporting_unit_get_units_construction_raceid(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['raceid'], '18525')

    def test_candidate_reporting_unit_get_units_construction_first(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['first'], 'Jack')

    def test_candidate_reporting_unit_get_units_construction_last(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['last'], 'Conway')

    def test_candidate_reporting_unit_get_units_construction_party(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['party'], 'Dem')

    def test_candidate_reporting_unit_get_units_construction_candidateid(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['candidateid'], '5266')

    def test_candidate_reporting_unit_get_units_construction_polid(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['polid'], '204')

    def test_candidate_reporting_unit_get_units_construction_ballotorder(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['ballotorder'], 1)

    def test_candidate_reporting_unit_get_units_construction_polnum(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['polnum'], '19601')

    def test_candidate_reporting_unit_get_units_construction_votecount(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['votecount'], 504)

    def test_candidate_reporting_unit_get_units_construction_winner(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['winner'], None)

    def test_candidate_reporting_unit_count(self):
        self.assertEqual(len(self.candidate_reporting_units), 505)

    def test_candidate_reporting_unit_sums_raceid(self):
        candidate_reporting_units = self.candidate_reporting_units[0:2]
        for cru in candidate_reporting_units:
            self.assertEqual(cru['raceid'], '7582')

    def test_candidate_reporting_unit_sums_level(self):
        candidate_reporting_units = self.candidate_reporting_units[0:2]
        for cru in candidate_reporting_units:
            self.assertEqual(cru['level'], 'state')

    def test_unique_ids(self):
        all_ids = list([b['id'] for b in self.candidate_reporting_units])
        unique_ids = set(all_ids)
        self.assertEqual(len(all_ids), len(unique_ids))

    def test_candidate_reporting_unit_get_units_construction_incumbent(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['incumbent'], None)

    def test_candidate_reporting_unit_get_units_construction_votepct(self):
        cru = self.candidate_reporting_units[(4 * 64) + 1]
        self.assertEqual(cru['votepct'], 0.45652173913043476)
