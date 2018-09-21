from datetime import date
from math import floor
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Task, Person, AverageIndexedMonthlyEarning, Earning, Money, MaximumTaxableEarning

class AverageIndexedMonthlyEarningTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)
		AverageIndexedMonthlyEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_years_for_highest_indexed_earnings=35)

	def test_calculate_for_person_that_worked_with_less_than_max_year(self):
		years_of_covered_earnings = 15
		taxable_earnings = []
		person = Person.objects.get(id=1)
		for i in range(0, years_of_covered_earnings):
			Earning.objects.create(money=Money.objects.create(amount=30000), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		max_tax_amount = Money.objects.create(amount=Decimal(118500))
		maxtax = MaximumTaxableEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_money=max_tax_amount)
		for earning in person.earning_set.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY):
			taxable_earnings.append(maxtax.calculate(earning))
		aime = AverageIndexedMonthlyEarning.objects.get(start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))
		self.assertAlmostEqual(1071.00, floor(aime.calculate(taxable_earnings=taxable_earnings)))

	# https://www.ssa.gov/oact/progdata/retirebenefit1.html
	def test_calculate_for_person_that_worked_with_more_than_max_year(self):
		person = Person.objects.get(id=1)
		Earning.objects.create(money=Money.objects.create(amount=45481), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=45623), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=45768), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=45912), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46053), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46196), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46342), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46484), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46629), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46772), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=46914), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47058), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47201), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47345), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47488), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47631), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47775), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=47918), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48062), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48206), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48350), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48492), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48636), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48780), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=48923), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49066), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49209), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49353), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49496), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49640), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49784), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=49927), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50070), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50213), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50357), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50500), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50644), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50787), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=50931), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		Earning.objects.create(money=Money.objects.create(amount=53880), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		max_tax_amount = Money.objects.create(amount=Decimal(118500))
		maxtax = MaximumTaxableEarning.objects.create(start_date=date(2018, 1, 1), end_date=date(2018, 12, 31), max_money=max_tax_amount)

		taxable_earnings = []
		for earning in person.earning_set.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY):
			taxable_earnings.append(maxtax.calculate(earning))
		aime = AverageIndexedMonthlyEarning.objects.get(start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))
		self.assertAlmostEqual(4060.00, floor(aime.calculate(taxable_earnings=taxable_earnings)))

	def test_stepByStep(self):
		years_of_covered_earnings = 15
		taxable_earnings = []
		person = Person.objects.get(id=1)
		for i in range(0, years_of_covered_earnings):
			Earning.objects.create(money=Money.objects.create(amount=30000), type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
		max_tax_amount = Money.objects.create(amount=Decimal(118500))
		maxtax = MaximumTaxableEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_money=max_tax_amount)
		for earning in person.earning_set.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY):
			taxable_earnings.append(maxtax.calculate(earning))
		aime = AverageIndexedMonthlyEarning.objects.get(start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))

		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get indexed yearly earnings', order=1)
		instruction.expression_set.create(description='indexed yearly earnings = ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00', order=1)
		instruction = expected_task.instruction_set.create(description='Sort indexed yearly earnings in descending order', order=2)
		instruction.expression_set.create(description='indexed yearly earnings = ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00', order=1)
		instruction = expected_task.instruction_set.create(description='Get highest 35 indexed yearly earnings', order=3)
		instruction.expression_set.create(description='highest 35 indexed yearly earnings = ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00, ' \
			'$30,000.00, $30,000.00, $30,000.00, $30,000.00, $30,000.00', order=1)
		instruction = expected_task.instruction_set.create(description='Get average indexed yearly earning', order=4)
		instruction.expression_set.create(description=f'average indexed yearly earning = sum of highest 35 indexed yearly earnings ' \
			'/ number of highest indexed yearly earnings', order=1)
		instruction.expression_set.create(description='average indexed yearly earning = $450,000.00 / 35', order=2)
		instruction.expression_set.create(description='average indexed yearly earning = $12,857.14', order=3)
		instruction = expected_task.instruction_set.create(description='Divide average indexed yearly earning by 12', order=5)
		instruction.expression_set.create(description='average indexed monthly earning = average indexed yearly earning / 12', order=1)
		instruction.expression_set.create(description='average indexed monthly earning = $12,857.14 / 12', order=2)
		instruction.expression_set.create(description='average indexed monthly earning = $1,071.43', order=3)

		self.assertEqual(expected_task, aime.stepByStep(taxable_earnings=taxable_earnings))