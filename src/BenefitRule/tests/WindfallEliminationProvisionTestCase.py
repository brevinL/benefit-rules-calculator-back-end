from datetime import date
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import WindfallEliminationProvision, Money, Task

class WindfallEliminationProvisionTestCase(TestCase):
	def setUp(self):
		WindfallEliminationProvision.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))

	def test_calculate(self):
		years_of_non_covered_earnings = 25
		wep = WindfallEliminationProvision.objects.get(start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))
		self.assertAlmostEqual(427.80,
			wep.calculate(
				primary_insurance_amount=Money(amount=839), 
				wep_primary_insurance_amount=Money(amount=411.20),
				monthly_non_covered_pension=Money(amount=1595.24)
			))

	def test_stepByStep(self):
		years_of_non_covered_earnings = 25
		wep = WindfallEliminationProvision.objects.get(start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31))

		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description="Get WEP's primary insurance amount", order=1)
		instruction.expression_set.create(description="WEP's primary insurance amount = primary insurance amount", order=1)
		instruction.expression_set.create(description="WEP's primary insurance amount = $411.20", order=2)

		instruction = expected_task.instruction_set.create(description="Get monthly non covered pension", order=2)
		instruction.expression_set.create(description="monthly non covered pension = $1,595.24", order=1)

		instruction = expected_task.instruction_set.create(description="Get primary insurance amount", order=3)
		instruction.expression_set.create(description="primary insurance amount = $839.00", order=1)

		instruction = expected_task.instruction_set.create(description='Find Windfall Elimination Provision reduction', order=4)
		instruction.expression_set.create(description='WEP reduction = min(monthly non covered pension x 1/2, max(primary insurance amount - WEP\'s primary insurance amount, 0))', order=1)
		instruction.expression_set.create(description='WEP reduction = min($1,595.24 x 1/2, max($839.00 - $411.20, 0))', order=2)
		instruction.expression_set.create(description='WEP reduction = min($797.62, max($427.80, 0)', order=3)
		instruction.expression_set.create(description='WEP reduction = min($797.62, $427.80)', order=4)
		instruction.expression_set.create(description='WEP reduction = $427.80', order=5)

		self.assertEqual(expected_task, wep.stepByStep(
			primary_insurance_amount=Money(amount=839), 
			wep_primary_insurance_amount=Money(amount=411.20),
			monthly_non_covered_pension=Money(amount=1595.24)
		))