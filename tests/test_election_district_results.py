try:
    set
except NameError:
    from sets import Set as set
import unittest

import maps
import tests
import utils


class TestElection(unittest.TestCase):

    data_url = 'tests/data/20160201_district_results.json'

    def setUp(self):
        self.electiondate, races = utils.open_file(self.data_url)
        self.candidate_reporting_units = utils.load_results(self.electiondate, races)

    def test_results_level(self):
        self.assertEqual(self.candidate_reporting_units[50]['level'], 'district')

    def test_number_of_parsed_races(self):
        races = set([r['raceid'] for r in self.candidate_reporting_units])
        self.assertEqual(len(races), 2)

    def test_race_attribute_construction_officeid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['officeid'], 'P')

    def test_race_attribute_construction_statepostal(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['statepostal'], 'IA')

    def test_race_attribute_construction_raceid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['raceid'], '16957')

    def test_race_attribute_construction_general(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['racetype'], 'Caucus')

    def test_race_attribute_construction_national(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['national'], True)

    def test_race_attribute_construction_officename(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['officename'], 'President')

    def test_race_attribute_construction_racetypeid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['racetypeid'], 'S')

    def test_race_get_units_construction_officeid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['officeid'], 'P')

    def test_race_get_units_construction_statepostal(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['statepostal'], 'IA')

    def test_race_get_units_construction_raceid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['raceid'], '16957')

    def test_race_get_units_construction_racetype(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['racetype'], 'Caucus')

    def test_race_get_units_construction_national(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['national'], True)

    def test_race_get_units_construction_officename(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['officename'], 'President')

    def test_race_get_units_construction_racetypeid(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual(race['racetypeid'], 'S')

    def test_existence_of_electiondate(self):
        race = self.candidate_reporting_units[-1]
        self.assertTrue(race.get('electiondate', False))

    def test_correct_electiondate(self):
        race = self.candidate_reporting_units[-1]
        self.assertEqual('2016-02-01', race['electiondate'])
