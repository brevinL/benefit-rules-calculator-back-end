from datetime import date
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import RetirementAge, Money, ordinal, currency, MIN_INTEGER, MAX_INTEGER

class RetirementAgeTestCase(TestCase):
	def setUp(self):
		nra = RetirementAge.objects.create(start_date=date.min, end_date=date.max,
			retirement_type=RetirementAge.NORMAL)
		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=MIN_INTEGER, end_year=1937, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=(65+2/12), start_year=1938, end_year=1942, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=66, start_year=1943, end_year=1954, 
			normal_retirement_age_change=0, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=(66+2/12), start_year=1955, end_year=1959, 
			normal_retirement_age_change=2/12, year_of_birth_change=1)
		nra.retirement_age_pieces.create(initial_retirement_age=67, start_year=1960, end_year=MAX_INTEGER, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		era = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.EARLIEST)
		era.retirement_age_pieces.create(initial_retirement_age=62, start_year=MIN_INTEGER, end_year=MAX_INTEGER, 
			normal_retirement_age_change=0, year_of_birth_change=1)

		dra = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
			retirement_type=RetirementAge.LATEST)
		dra.retirement_age_pieces.create(initial_retirement_age=70, start_year=MIN_INTEGER, end_year=MAX_INTEGER, 
			normal_retirement_age_change=0, year_of_birth_change=1)

	def test_calculate_normal_retirement_age(self):
		nra = RetirementAge.objects.get(
			retirement_type=RetirementAge.NORMAL,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(65, nra.calculate(year_of_birth=1930))
		self.assertAlmostEqual(65, nra.calculate(year_of_birth=1937))
		self.assertAlmostEqual(65 + 2/12, nra.calculate(year_of_birth=1938))
		self.assertAlmostEqual(65 + 4/12, nra.calculate(year_of_birth=1939))
		self.assertAlmostEqual(65 + 6/12, nra.calculate(year_of_birth=1940))
		self.assertAlmostEqual(65 + 8/12, nra.calculate(year_of_birth=1941))
		self.assertAlmostEqual(65 + 10/12, nra.calculate(year_of_birth=1942))
		self.assertAlmostEqual(66, nra.calculate(year_of_birth=1943))
		self.assertAlmostEqual(66, nra.calculate(year_of_birth=1950))
		self.assertAlmostEqual(66, nra.calculate(year_of_birth=1954))
		self.assertAlmostEqual(66 + 2/12, nra.calculate(year_of_birth=1955))
		self.assertAlmostEqual(66 + 4/12, nra.calculate(year_of_birth=1956))
		self.assertAlmostEqual(66 + 6/12, nra.calculate(year_of_birth=1957))
		self.assertAlmostEqual(66 + 8/12, nra.calculate(year_of_birth=1958))
		self.assertAlmostEqual(66 + 10/12, nra.calculate(year_of_birth=1959))
		self.assertAlmostEqual(67, nra.calculate(year_of_birth=1960))
		self.assertAlmostEqual(67, nra.calculate(year_of_birth=2017))

	def test_calculate_early_retirement_age(self):
		era = RetirementAge.objects.get(
			retirement_type=RetirementAge.EARLIEST,
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(62, era.calculate(year_of_birth=1930))
		self.assertAlmostEqual(62, era.calculate(year_of_birth=1960))
		self.assertAlmostEqual(62, era.calculate(year_of_birth=2017))

	def test_calculate_delayed_retirement_age(self):
		dra = RetirementAge.objects.get(
			retirement_type=RetirementAge.LATEST,
			start_date__lte=date(2016, 1, 1),
			end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(70, dra.calculate(year_of_birth=1930))
		self.assertAlmostEqual(70, dra.calculate(year_of_birth=1960))
		self.assertAlmostEqual(70, dra.calculate(year_of_birth=2017))