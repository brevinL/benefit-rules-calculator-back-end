from datetime import date
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import GovernmentPensionOffset, Money, Task

class GovernmentPensionOffsetTestCase(TestCase):
	def setUp(self):
		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

	def test_calculate(self):
		gpo = GovernmentPensionOffset.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		self.assertAlmostEqual(600 * 2/3, gpo.calculate(monthly_non_covered_pension=Money(amount=600)))

	def test_stepByStep(self):
		gpo = GovernmentPensionOffset.objects.get(
			start_date__lte=date(2016, 1, 1), end_date__gte=date(2016, 12, 31)
		)
		
		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get monthly non covered pension', order=1)
		instruction.expression_set.create(description='monthly non covered pension = $600.00', order=1)
		instruction = expected_task.instruction_set.create(description='Get offset', order=2)
		instruction.expression_set.create(description='offset = 2/3', order=1)
		instruction = expected_task.instruction_set.create(description='Multiply the monthly non covered pension with the offset', order=3)
		instruction.expression_set.create(description='government pension offset = monthly non covered pension x offset', order=1)
		instruction.expression_set.create(description='government pension offset = $600.00 x 2/3', order=2)
		instruction.expression_set.create(description='government pension offset = $400.00', order=3)

		self.assertEqual(expected_task, gpo.stepByStep(monthly_non_covered_pension=Money(amount=600)))