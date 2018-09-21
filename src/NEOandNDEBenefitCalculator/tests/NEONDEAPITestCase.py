# from datetime import date
# from math import inf
# import json
# from django.urls import reverse
# from rest_framework.test import APITestCase, APIRequestFactory
# from BenefitRule.models import *
# from NEOandNDEBenefitCalculator.models import *
# from NEOandNDEBenefitCalculator.serializers import *
# from NEOandNDEBenefitCalculator.views import CalculatorViewSet

# # test to not confuse the rules in this module vs the BenefitRule.models
# class NEONDEAPITestCase(APITestCase):
# 	fixtures = ['CoveredEarning.json', 'NonCoveredEarning.json', 'Money.json', 'Person.json']

# 	data_request = {
# 		'respondents': [
# 			{
# 				'year_of_birth': 1954,
# 				'years_of_covered_earnings': 15,
# 				'annual_covered_earning': {'amount': 30000.00},
# 				'years_of_non_covered_earnings': 25,
# 				'annual_non_covered_earning': {'amount': 40000.00},
# 				'fraction_of_non_covered_aime_to_non_covered_pension': 0.67,
# 				'early_retirement_reduction': 0.00,
# 				'delay_retirement_credit': 0.00,
# 				'spousal_early_retirement_reduction': 0.00,
# 				'survivor_early_retirement_reduction': 0.00
# 			},
# 			{
# 				'year_of_birth': 1954,
# 				'years_of_covered_earnings': 40,
# 				'annual_covered_earning': {'amount': 50000.00},
# 				'years_of_non_covered_earnings': 0,
# 				'annual_non_covered_earning': {'amount': 0.00},
# 				'fraction_of_non_covered_aime_to_non_covered_pension': 0.67,
# 				'early_retirement_reduction': 0.00,
# 				'delay_retirement_credit': 0.00,
# 				'spousal_early_retirement_reduction': 0.00,
# 				'survivor_early_retirement_reduction': 0.00
# 			}
# 		],
# 		'relationships': [
# 			{
# 				'person1_id': 1,
# 				'person2_id': 2,
# 				'relationship_type': 'M'
# 			}
# 		]
# 	}

# 	def setUp(self):
# 		nra = RetirementAge.objects.create(start_date=date.min, end_date=date.max,
# 			retirement_type=RetirementAge.NORMAL)
# 		nra.retirement_age_pieces.create(initial_retirement_age=65, start_year=-inf, end_year=1937, 
# 			normal_retirement_age_change=0, year_of_birth_change=1)
# 		nra.retirement_age_pieces.create(initial_retirement_age=(65+2/12), start_year=1938, end_year=1942, 
# 			normal_retirement_age_change=2/12, year_of_birth_change=1)
# 		nra.retirement_age_pieces.create(initial_retirement_age=66, start_year=1943, end_year=1954, 
# 			normal_retirement_age_change=0, year_of_birth_change=1)
# 		nra.retirement_age_pieces.create(initial_retirement_age=(66+2/12), start_year=1955, end_year=1959, 
# 			normal_retirement_age_change=2/12, year_of_birth_change=1)
# 		nra.retirement_age_pieces.create(initial_retirement_age=67, start_year=1960, end_year=inf, 
# 			normal_retirement_age_change=0, year_of_birth_change=1)

# 		era = RetirementAge.objects.create(start_date=date.min, end_date=date.max, 
# 			retirement_type=RetirementAge.EARLIEST)
# 		era.retirement_age_pieces.create(initial_retirement_age=62, start_year=-inf, end_year=inf, 
# 			normal_retirement_age_change=0, year_of_birth_change=1)

# 		SurvivorInsuranceBenefit.objects.create(start_date=date.min, end_date=date.max, max_benefit_entitlement_factor=0.825)

# 		err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
# 			benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
# 		err.early_retirement_benefit_reduction_piece_set.create(factor=5/9, percentage=0.01, theshold_in_months=36)
# 		err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=inf)

# 		spousal_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
# 			benefit_type=EarlyRetirementBenefitReduction.SPOUSAL)
# 		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=25/36, percentage=0.01, theshold_in_months=36)
# 		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=inf)

# 		survivor_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
# 			benefit_type=EarlyRetirementBenefitReduction.SURVIVOR)
# 		survivor_err.survivor_early_retirement_benefit_reduction_piece_set.create(max_percentage_reduction=0.285)

# 		SpousalInsuranceBenefit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)

# 		GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

# 		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70.0)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
# 		DelayRetirementCreditPiece.objects.create(inital_percentage=0.08, min_year=1943, max_year=inf, percentage_rate=0, year_change=1, delay_retirement_credit=drc)

# 		WindfallEliminationProvision.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))

# 		AverageIndexedMonthlyEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_years_for_highest_indexed_earnings=35)

# 		pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31),
# 			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC)
# 		BendPoint.objects.create(min_dollar_amount=-inf, max_dollar_amount=856, order=1, primary_insurance_amount=pia)
# 		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=pia)
# 		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=inf, order=3, primary_insurance_amount=pia)

# 		f1 = Factor.objects.create(order=1, primary_insurance_amount=pia)
# 		FactorPiece.objects.create(inital_factor=0.90, order=1, factor=f1)

# 		f2 = Factor.objects.create(order=2, primary_insurance_amount=pia)
# 		FactorPiece.objects.create(inital_factor=0.32, order=1, factor=f2)

# 		f3 = Factor.objects.create(order=3, primary_insurance_amount=pia)
# 		FactorPiece.objects.create(inital_factor=0.15, order=1, factor=f3)

# 		wep_pia = PrimaryInsuranceAmount.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31),
# 			type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP)
# 		BendPoint.objects.create(min_dollar_amount=-inf, max_dollar_amount=856, order=1, primary_insurance_amount=wep_pia)
# 		BendPoint.objects.create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=wep_pia)
# 		BendPoint.objects.create(min_dollar_amount=5157, max_dollar_amount=inf, order=3, primary_insurance_amount=wep_pia)

# 		f1 = Factor.objects.create(order=1, primary_insurance_amount=wep_pia)
# 		FactorPiece.objects.create(inital_factor=0.40, min_year_of_coverage=-inf, max_year_of_coverage=20, order=1, factor=f1)
# 		FactorPiece.objects.create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f1)
# 		FactorPiece.objects.create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=inf, order=3, factor=f1)

# 		f2 = Factor.objects.create(order=2, primary_insurance_amount=wep_pia)
# 		FactorPiece.objects.create(inital_factor=0.32, order=1, factor=f2)

# 		f3 = Factor.objects.create(order=3, primary_insurance_amount=wep_pia)
# 		FactorPiece.objects.create(inital_factor=0.15, order=1, factor=f3)

# 		max_tax_amount = Money.objects.create(amount=Decimal(118500))
# 		MaximumTaxableEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_money=max_tax_amount)

# 	def test_summary(self):
# 		factory = APIRequestFactory()
# 		url = '/api/neo-and-neo-benefit-calculator/summary' # reverse('life-table-api:lifetable-Sx')
# 		request = factory.post(url, self.data_request, format='json') 
# 		neo_and_ndr_benefit_calculator_summary_view = CalculatorViewSet.as_view({'post': 'summary'})
# 		response = neo_and_ndr_benefit_calculator_summary_view(request)
# 		# https://realpython.com/test-driven-development-of-a-django-restful-api/
# 		records = [
# 			{
# 				'person_id': 1,
# 				'year_of_birth': 1954,
# 				'earliest_retirement_age': 62,
# 				'normal_retirement_age': 66,
# 				'average_indexed_monthly_covered_earning': {'amount': 1071.43},
# 				'basic_primary_insurance_amount': {'amount': 839.30},
# 				'wep_primary_insurance_amount': {'amount': 411.30},
# 				'average_indexed_monthly_non_covered_earning': {'amount': 2380.95},
# 				'monthly_non_covered_pension': {'amount': 1595.24},
# 				'wep_reduction': {'amount': 428.00},
# 				'final_primary_insurance_amount': {'amount': 411.30},
# 				'delay_retirement_credit': 0.00,
# 				'early_retirement_reduction': 0.00,
# 				'benefit': {'amount': 411.30},
# 				'government_pension_offset': {'amount': 1063.49},
# 				'spousal_insurance_benefit': {'amount': 0.00},
# 				'survivor_insurance_benefit': {'amount': 355.01}
# 			},
# 			{
# 				'person_id': 2,
# 				'year_of_birth': 1954,
# 				'earliest_retirement_age': 62,
# 				'normal_retirement_age': 66,
# 				'average_indexed_monthly_covered_earning': {'amount': 4166.67},
# 				'basic_primary_insurance_amount': {'amount': 1829.80},
# 				'wep_primary_insurance_amount': {'amount': 1829.80},
# 				'average_indexed_monthly_non_covered_earning': {'amount': 0.00},
# 				'monthly_non_covered_pension': {'amount': 0.00},
# 				'wep_reduction': {'amount': 0.00},
# 				'final_primary_insurance_amount': {'amount': 1829.80},
# 				'delay_retirement_credit': 0.00,
# 				'early_retirement_reduction': 0.00,
# 				'benefit': {'amount': 1829.80},
# 				'government_pension_offset': {'amount': 0.00},
# 				'spousal_insurance_benefit': {'amount': 0.00},
# 				'survivor_insurance_benefit': {'amount': 0.00}
# 			}
# 		]
# 		serializer = RecordSerializer(records, many=True)
# 		expected_response = {'records': serializer.data}
# 		# self.maxDiff = None
# 		self.assertEqual(response.data, expected_response)

# 	def requestStepByStepInstructions(self):
# 		factory = APIRequestFactory()
# 		url = '/api/neo-and-neo-benefit-calculator/stepByStep' # reverse('life-table-api:lifetable-Sx')
# 		request = factory.post(url, self.data_request, format='json') 
# 		neo_and_ndr_benefit_calculator_stepByStep_view = CalculatorViewSet.as_view({'post': 'stepByStep'})
# 		return neo_and_ndr_benefit_calculator_stepByStep_view(request)

# 	def test_stepByStep_has_same_numbers_of_records_as_requested_respondents(self):
# 		response = self.requestStepByStepInstructions()
# 		self.assertEqual(len(self.data_request['respondents']), len(response.data['detail_records']))

# 	def test_stepByStep_average_indexed_monthly_covered_earning_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		maxtax = MaximumTaxableEarning.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		aime = AverageIndexedMonthlyEarning.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		covered_earnings = Earning.objects.filter(
# 			type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
# 		taxable_covered_earnings = []
# 		for covered_earning in covered_earnings:
# 			taxable_covered_earnings.append(maxtax.calculate(covered_earning))
# 		stepByStep = {'person_id': person.id, 
# 			'average_indexed_monthly_covered_earning_instructions': aime.stepByStep(taxable_earnings=taxable_covered_earnings)}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['average_indexed_monthly_covered_earning_instructions'], 
# 			expected_response['detail_record']['average_indexed_monthly_covered_earning_instructions'])

# 	def test_stepByStep_basic_primary_insurance_amount_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		basic_pia = PrimaryInsuranceAmount.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)),
# 			type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC
# 		)
# 		stepByStep = {'person_id': person.id, 
# 			'basic_primary_insurance_amount_instructions': 
# 				basic_pia.stepByStep(average_indexed_monthly_earning=Money(amount=Decimal(1071.43)), year_of_coverage=0)}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['basic_primary_insurance_amount_instructions'], 
# 			expected_response['detail_record']['basic_primary_insurance_amount_instructions'])

# 	def test_stepByStep_wep_primary_insurance_amount_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		wep_pia = PrimaryInsuranceAmount.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)),
# 			type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP
# 		)
# 		stepByStep = {'person_id': person.id, 
# 			'wep_primary_insurance_amount_instructions': 
# 				wep_pia.stepByStep(average_indexed_monthly_earning=Money(amount=Decimal(1071.43)), year_of_coverage=15)}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['wep_primary_insurance_amount_instructions'], 
# 			expected_response['detail_record']['wep_primary_insurance_amount_instructions'])

# 	def test_stepByStep_average_indexed_monthly_non_covered_earning_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		maxtax = MaximumTaxableEarning.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		aime = AverageIndexedMonthlyEarning.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		non_covered_earnings = Earning.objects.filter(
# 			type_of_earning=Earning.NONCOVERED, time_period=Earning.YEARLY, person=person)
# 		taxable_non_covered_earnings = []
# 		for non_covered_earning in non_covered_earnings: # does maxtax return decimal or just float/int?
# 			taxable_non_covered_earnings.append(maxtax.calculate(non_covered_earning))
# 		stepByStep = {'person_id': person.id, 
# 			'average_indexed_monthly_non_covered_earning_instructions': aime.stepByStep(taxable_earnings=taxable_non_covered_earnings)}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['average_indexed_monthly_non_covered_earning_instructions'], 
# 			expected_response['detail_record']['average_indexed_monthly_non_covered_earning_instructions'])

# 	def test_stepByStep_monthly_non_covered_pension_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		instructions = [
# 			Instruction(description='Get average indexed monthly non covered earning',
# 				expressions=[f'average indexed monthly non covered earning = $2,380.95']),
# 			Instruction(description='Get fraction of non covered AIME to non covered pension',
# 				expressions=[f'fraction of non covered AIME to non covered pension = 0.67']),
# 			Instruction(description='Multiply average indexed monthly non covered earning with the fraction that was coverted from non covered AIME to non covered pension', 
# 				expressions=[
# 					'monthly_non_covered_pension = average indexed monthly non covered earning x fraction of non covered AIME to non covered pension',
# 					f'monthly_non_covered_pension = $2,380.95 x 0.67',
# 					f'monthly_non_covered_pension = $1,595.24'])] 
# 		stepByStep = {'person_id': person.id, 
# 			'monthly_non_covered_pension_instructions': instructions}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['monthly_non_covered_pension_instructions'], 
# 			expected_response['detail_record']['monthly_non_covered_pension_instructions'])

# 	def test_stepByStep_wep_reduction_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		wep = WindfallEliminationProvision.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		stepByStep = {'person_id': person.id, 
# 			'wep_reduction_instructions': wep.stepByStep(
# 				primary_insurance_amount=Money(amount=Decimal(839.30)), 
# 				wep_primary_insurance_amount=Money(amount=Decimal(411.30)),
# 				monthly_non_covered_pension=Money(amount=Decimal(1595.24)))}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['wep_reduction_instructions'], 
# 			expected_response['detail_record']['wep_reduction_instructions'])

# 	def test_stepByStep_final_primary_insurance_amount_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		instructions = [
# 			Instruction(description='Get primary insurance amount', expressions=[f'primary insurance amount = $839.30']),
# 			Instruction(description='Get windfall elimination provision amount', expressions=[f'windfall elimination provision amount = $428.00']),
# 			Instruction(description='Recalculate primary insurance amount by reducing the primary insurance amount with the windfall elimination provision amount', 
# 				expressions=[
# 					'primary insurance amount  = primary insurance amount - windfall elimination provision',
# 					f'primary insurance amount  = $839.30 - $428.00',
# 					f'primary insurance amount = $411.30'])]
# 		stepByStep = {'person_id': person.id, 
# 			'final_primary_insurance_amount_instructions': instructions}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['final_primary_insurance_amount_instructions'], 
# 			expected_response['detail_record']['final_primary_insurance_amount_instructions'])

# 	def test_stepByStep_delay_retirement_credit_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		drc = DelayRetirementCredit.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		instructions = drc.stepByStep(year_of_birth=1954, normal_retirement_age=66.0, delayed_retirement_age=70.0)
# 		instructions.append(
# 			Instruction(description='Get respondent\'s delay retirement credit',
# 				expressions=['respondent\'s delay retirement credit = 0.00%']))
# 		instructions.append(
# 			Instruction(description='Cap Delay Retirement Credit', 
# 				expressions=[
# 					'delay retirement credit = min(max delay retirement credit, respondent\'s delay retirement credit',
# 					'delay retirement credit = min(40.00%, 0.00%)',
# 					'delay retirement credit = 0.00%']))
# 		stepByStep = {'person_id': person.id, 
# 			'delay_retirement_credit_instructions': instructions} 
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['delay_retirement_credit_instructions'], 
# 			expected_response['detail_record']['delay_retirement_credit_instructions'])

# 	def test_stepByStep_early_retirement_reduction_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		err = EarlyRetirementBenefitReduction.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)) &
# 			Q(benefit_type=EarlyRetirementBenefitReduction.PRIMARY))
# 		instructions = err.stepByStep(normal_retirement_age=66.0, early_retirement_age=62.0)
# 		instructions.append(
# 			Instruction(description='Get respondent\'s early retirement reduction',
# 				expressions=['respondent\'s early retirement reduction = 0.00%']))
# 		instructions.append(
# 			Instruction(description='Cap Delay Retirement Credit', 
# 				expressions=[
# 					'early retirement reduction = min(max early retirement reduction, respondent\'s early retirement reduction',
# 					'early retirement reduction = min(25.00%, 0.00%)',
# 					'early retirement reduction = 0.00%']))
# 		stepByStep = {'person_id': person.id, 
# 			'early_retirement_reduction_instructions': instructions} 
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['early_retirement_reduction_instructions'], 
# 			expected_response['detail_record']['early_retirement_reduction_instructions'])

# 	def test_stepByStep_benefit_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		instructions = [
# 			Instruction(description='Get delay retirement credit', expressions=[f'delay retirement credit = 0.00%']),
# 			Instruction(description='Get early retirement reduction', expressions=[f'early retirement reduction = 0.00%']),
# 			Instruction(description='Get primary insurance amount', expressions=[f'primary insurance amount = $411.30']),
# 			Instruction(description='Calculate benefit', expressions=[
# 				'benefit = primary insurance amount x (1 + (delay retirement credit + early retirement reduction))',
# 				f'benefit = $411.30 x (1 + (0.00% + 0.00%))',
# 				f'benefit = $411.30 x 100.00%',
# 				f'benefit = $411.30'])]
# 		stepByStep = {'person_id': person.id, 
# 			'benefit_instructions': instructions}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['benefit_instructions'], 
# 			expected_response['detail_record']['benefit_instructions'])

# 	def test_stepByStep_government_pension_offset_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		gpo = GovernmentPensionOffset.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		stepByStep = {'person_id': person.id, 
# 			'government_pension_offset_instructions': gpo.stepByStep(monthly_non_covered_pension=Money(amount=Decimal(1595.24)))}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['government_pension_offset_instructions'], 
# 			expected_response['detail_record']['government_pension_offset_instructions'])

# 	def test_stepByStep_spousal_insurance_benefit_instructions(self):
# 		response = self.requestStepByStepInstructions()

# 		year = 2016
# 		person = Person.objects.get(id=1)
# 		spousal_insurance_benefit_law = SpousalInsuranceBenefit.objects.get(
# 			Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 		stepByStep = {'person_id': person.id, 
# 			'spousal_insurance_benefit_instructions': spousal_insurance_benefit_law.stepByStep(
# 			primary_insurance_amount=Money(amount=Decimal(839.30)), 
# 			spousal_primary_insurance_amount=Money(amount=Decimal(1829.80)),
# 			government_pension_offset=Money(amount=Decimal(1063.49)))}
# 		serializer = DetailRecordSerializer(stepByStep)
# 		expected_response = {'detail_record': serializer.data}

# 		self.assertEqual(response.data['detail_records'][0]['spousal_insurance_benefit_instructions'], 
# 			expected_response['detail_record']['spousal_insurance_benefit_instructions'])

# 	# def test_stepByStep_survivor_insurance_benefit_instructions(self):
# 	# 	response = self.requestStepByStepInstructions()

# 	# 	year = 2016
# 	# 	person = Person.objects.get(id=1)
# 	# 	maxtax = MaximumTaxableEarning.objects.get(
# 	# 		Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 	# 	aime = AverageIndexedMonthlyEarning.objects.get(
# 	# 		Q(start_date__lte=date(year, 1, 1)) & Q(end_date__gte=date(year, 12, 31)))
# 	# 	covered_earnings = Earning.objects.filter(
# 	# 		type_of_earning=Earning.COVERED, time_period=Earning.YEARLY, person=person)
# 	# 	taxable_covered_earnings = []
# 	# 	for covered_earning in covered_earnings:
# 	# 		taxable_covered_earnings.append(maxtax.calculate(covered_earning))
# 	# 	stepByStep = {'person_id': person.id, 
# 	# 		'average_indexed_monthly_covered_earning_instructions': aime.stepByStep(taxable_earnings=taxable_covered_earnings)}
# 	# 	serializer = DetailRecordSerializer(stepByStep)
# 	# 	expected_response = {'detail_record': serializer.data}

# 	# 	self.assertEqual(response.data['detail_records'][0]['average_indexed_monthly_covered_earning_instructions'], 
# 	# 		expected_response['detail_record']['average_indexed_monthly_covered_earning_instructions'])