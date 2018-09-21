from datetime import date
from math import inf, floor
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Person, SpousalInsuranceBenefit, Money, Task

class SpousalInsuranceBenefitTestCase(TestCase):
	def setUp(self):
		Person.objects.create(id=1, year_of_birth=1954)
		Person.objects.create(id=2, year_of_birth=1954)
		SpousalInsuranceBenefit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)

	def test_isEntitled_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		primary_insurance_amount = Money(amount=411)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertTrue(spousal_insurance_benefit.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount))

	def test_isEntitled_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		primary_insurance_amount = Money(amount=1000)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertFalse(spousal_insurance_benefit.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount))

	def test_maxEntitlement(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		spousal_primary_insurance_amount = Money(amount=1829)
		self.assertAlmostEqual(914.5, spousal_insurance_benefit.maxEntitlement(spousal_primary_insurance_amount))

	def test_calculate_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(22.50, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=679), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))

		self.assertAlmostEqual(0, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=1064)))

	def test_calculate_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(0, spousal_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=1064)))

	def test_stepByStep_is_not_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)

		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get spousal\' primary insurance amount', order=1)
		instruction.expression_set.create(description='spousal\'s primary insurance amount = $1,829.00', order=1)
		instruction = expected_task.instruction_set.create(description='Calculate the maximum entitlement to spousal insurance benefit', order=2)
		instruction.expression_set.create(description='maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor', order=1)
		instruction.expression_set.create(description='maximum benefit entitlement = $1,829.00 x 1/2', order=2)
		instruction.expression_set.create(description='maximum benefit entitlement = $914.50', order=3)
		instruction = expected_task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description='primary insurance amount = $1,000.00', order=1)
		instruction = expected_task.instruction_set.create(description='Determine if person is entitled to spousal insurance benefit', order=4)
		instruction.expression_set.create(description='primary insurance amount < maximum benefit entitlement?', order=1)
		instruction.expression_set.create(description='$1,000.00 < $914.50?', order=2)
		instruction.expression_set.create(description='False', order=3)
		instruction = expected_task.instruction_set.create(description='Set spousal insurance benefit to zero', order=5)
		instruction.expression_set.create(description='spousal insurance benefit = $0.00', order=1)

		self.assertEqual(expected_task, spousal_insurance_benefit.stepByStep(
			primary_insurance_amount=Money(amount=1000), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))

	def test_stepByStep_is_entitled(self):
		spousal_insurance_benefit = SpousalInsuranceBenefit.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)

		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get spousal\' primary insurance amount', order=1)
		instruction.expression_set.create(description='spousal\'s primary insurance amount = $1,829.00', order=1)

		instruction = expected_task.instruction_set.create(description='Calculate the maximum entitlement to spousal insurance benefit', order=2)
		instruction.expression_set.create(description='maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor', order=1)
		instruction.expression_set.create(description='maximum benefit entitlement = $1,829.00 x 1/2', order=2)
		instruction.expression_set.create(description='maximum benefit entitlement = $914.50', order=3)

		instruction = expected_task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description='primary insurance amount = $679.00', order=1)

		instruction = expected_task.instruction_set.create(description='Determine if person is entitled to spousal insurance benefit', order=4)
		instruction.expression_set.create(description='primary insurance amount < maximum benefit entitlement?', order=1)
		instruction.expression_set.create(description='$679.00 < $914.50?', order=2)
		instruction.expression_set.create(description='True', order=3)

		instruction = expected_task.instruction_set.create(description='Set spousal insurance benefit to maximum benefit entitlement', order=5)
		instruction.expression_set.create(description='spousal insurance benefit = maximum benefit entitlement', order=1)
		instruction.expression_set.create(description='spousal insurance benefit = $914.50', order=2)

		instruction = expected_task.instruction_set.create(description='Subtract the primary insurance amount from spousal insurance benefit', order=6)
		instruction.expression_set.create(description='spousal insurance benefit = spousal insurance benefit - primary insurance amount', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = $914.50 - $679.00', order=2)
		instruction.expression_set.create(description=f'spousal insurance benefit = $235.50', order=3)

		instruction = expected_task.instruction_set.create(description='Get government pension offset', order=7)
		instruction.expression_set.create(description=f'government pension offset = $213.00', order=1)

		instruction = expected_task.instruction_set.create(description='Subtract the government pension offset from spousal insurance benefit', order=8)
		instruction.expression_set.create(description='spousal insurance benefit = spousal insurance benefit - government pension offset', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = $235.50 - $213.00', order=2)
		instruction.expression_set.create(description=f'spousal insurance benefit = $22.50', order=3)

		instruction = expected_task.instruction_set.create(description='Cap spousal insurance benefit', order=9)
		instruction.expression_set.create(description='spousal insurance benefit = max($0.00, spousal insurance benefit)', order=1)
		instruction.expression_set.create(description='spousal insurance benefit = max($0.00, $22.50)', order=2)
		instruction.expression_set.create(description='spousal insurance benefit = $22.50', order=3)

		self.assertEqual(expected_task, spousal_insurance_benefit.stepByStep(
			primary_insurance_amount=Money(amount=679), 
			spousal_primary_insurance_amount=Money(amount=1829), 
			government_pension_offset=Money(amount=213)))