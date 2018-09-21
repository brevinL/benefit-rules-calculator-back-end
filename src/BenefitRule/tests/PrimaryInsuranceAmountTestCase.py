from datetime import date
from django.test import TestCase
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import Money, Task, PrimaryInsuranceAmount, BendPoint, Factor, FactorPiece, MIN_POSITIVE_INTEGER, MAX_POSITIVE_INTEGER

class PrimaryInsuranceAmountTestCase(TestCase):
	def setUp(self):
		pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC)
		BendPoint.objects.create(min_dollar_amount=MIN_POSITIVE_INTEGER, max_dollar_amount=856, order=1, primary_insurance_amount=pia)
		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=pia)
		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=MAX_POSITIVE_INTEGER, order=3, primary_insurance_amount=pia)

		f1 = Factor.objects.create(order=1, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
			year_of_coverage_change=1, factor_change=0, order=1, factor=f1)

		f2 = Factor.objects.create(order=2, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.32, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
			year_of_coverage_change=1, factor_change=0, order=1, factor=f2)

		f3 = Factor.objects.create(order=3, primary_insurance_amount=pia)
		FactorPiece.objects.create(inital_factor=0.15, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
			year_of_coverage_change=1, factor_change=0, order=1, factor=f3)

		wep_pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP)
		BendPoint.objects.create(min_dollar_amount=MIN_POSITIVE_INTEGER, max_dollar_amount=856, order=1, primary_insurance_amount=wep_pia)
		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=wep_pia)
		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=MAX_POSITIVE_INTEGER, order=3, primary_insurance_amount=wep_pia)

		f1 = Factor.objects.create(order=1, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.40, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=20, year_of_coverage_change=1, factor_change=0, order=1, factor=f1)
		FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f1)
		FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=MAX_POSITIVE_INTEGER, year_of_coverage_change=1, factor_change=0, order=3, factor=f1)

		f2 = Factor.objects.create(order=2, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.32, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
			year_of_coverage_change=1, factor_change=0, order=1, factor=f2)

		f3 = Factor.objects.create(order=3, primary_insurance_amount=wep_pia)
		FactorPiece.objects.create(inital_factor=0.15, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
			year_of_coverage_change=1, factor_change=0, order=1, factor=f3)

	def test_calculate_normal_pia_within_parameter(self):
		pia = PrimaryInsuranceAmount.objects.get(
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		self.assertAlmostEqual(839.20, pia.calculate(average_indexed_monthly_earning=1071, year_of_coverage=0))

	def test_calculate_wep_pia_within_parameter(self):
		wep_pia = PrimaryInsuranceAmount.objects.get(
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP
		)
		self.assertAlmostEqual(411.20, wep_pia.calculate(average_indexed_monthly_earning=1071, year_of_coverage=15))

	def test_factors_order(self):
		pia = PrimaryInsuranceAmount.objects.get(
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		result = []
		for factor in pia.factors.all():
			result.append(factor.calculate(year_of_coverage=0))
		self.assertEqual([0.90, 0.32, 0.15], result)

	def test_stepByStep(self):
		pia = PrimaryInsuranceAmount.objects.get(
			start_date__lte=date(2016, 1, 1), 
			end_date__gte=date(2016, 12, 31),
			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
		)
		first_pia_factor = max(0, 0 + 0.9 * ( min(1071, 856) - 0 ))
		second_pia_factor = max(0, 0.32 * ( min(1071, 5157) - 856 ))
		third_pia_factor = max(0, 0.15 * ( min(1071, 0) - 5157 ))

		expected_task = Task.objects.create()
		instruction = expected_task.instruction_set.create(description='Get average indexed monthly earning', order=1)
		instruction.expression_set.create(description='average indexed monthly earning = $1,071.00', order=1)
		instruction = expected_task.instruction_set.create(description='Initalize total primary insurance amount to 0', order=2)
		instruction.expression_set.create(description='primary insurance amount = $0.00', order=1)
		instruction = expected_task.instruction_set.create(description='Add 90.0 percent his/her average indexed monthly ' \
			'earning up to $856.00 to total primary insurance amount', order=3)
		instruction.expression_set.create(description='primary insurance amount = primary insurance amount + ' \
			'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))', order=1)
		instruction.expression_set.create(description='primary insurance amount = max($0.00, $0.00 + 0.9 x ( min($1,071.00, $856.00) - $0.00 ))', order=2)
		instruction.expression_set.create(description='primary insurance amount = $770.40', order=3),
		instruction = expected_task.instruction_set.create(description='Add 32.0 percent his/her average indexed monthly ' \
			'earning between $856.00 and $5,157.00 to total primary insurance amount', order=4)
		instruction.expression_set.create(description='primary insurance amount = primary insurance amount + ' \
			'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))', order=1)
		instruction.expression_set.create(description='primary insurance amount = max($0.00, $770.40 + 0.32 x ' \
			'( min($1,071.00, $5,157.00) - $856.00 ))', order=2)
		instruction.expression_set.create(description='primary insurance amount = $839.20', order=3),
		instruction = expected_task.instruction_set.create(description='Add 15.0 percent his/her average indexed monthly ' \
			'earning above $5,157.00 to total primary insurance amount', order=5)
		instruction.expression_set.create(description='primary insurance amount = primary insurance amount + ' \
			'max($0.00, factor x ( min(average indexed monthly earning, minimum dollar amount threshold) - maximum dollar amount threshold ))', order=1)
		instruction.expression_set.create(description='primary insurance amount = max($0.00, $839.20 + ' \
			'0.15 x ( min($1,071.00, $0.00) - $5,157.00 ))', order=2)
		instruction.expression_set.create(description='primary insurance amount = $839.20', order=3),
		instruction = expected_task.instruction_set.create(description='Round total primary insurance amount to the next lower multiple of $0.10 ' \
			'if it is not already a multiple of $0.10', order=6)
		instruction.expression_set.create(description='primary insurance amount = floor(primary insurance amount * 10) / 10', order=1)
		instruction.expression_set.create(description='primary insurance amount = floor($839.20 * 10) / 10', order=2)
		instruction.expression_set.create(description='primary insurance amount = $839.20', order=3)
		
		primary_insurance_amount_task = pia.stepByStep(average_indexed_monthly_earning=Money(amount=1071), year_of_coverage=0)
		for expected_instruction in expected_task.instruction_set.all():
			pia_instruction = primary_insurance_amount_task.instruction_set.get(order=expected_instruction.order)
			self.assertEqual(pia_instruction, expected_instruction)

			for expected_expression in expected_instruction.expression_set.all():
				pia_expression = pia_instruction.expression_set.get(order=expected_expression.order)
				self.assertEqual(pia_expression, expected_expression)