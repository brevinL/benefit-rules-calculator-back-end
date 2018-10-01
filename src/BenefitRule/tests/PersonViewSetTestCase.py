from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIRequestFactory
from BenefitRule.views import PersonViewSet
from BenefitRule.models import *
from BenefitRule.serializers import RecordSerializer, DetailRecordSerializer

class PersonViewSetTestCase(APITestCase):
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

		survivor_insurance_benefit = SurvivorInsuranceBenefit.objects.create(start_date=date.min, end_date=date.max, max_benefit_entitlement_factor=0.825)

		err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/9, percentage=0.01, theshold_in_months=36)
		err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)

		spousal_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SPOUSAL)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=25/36, percentage=0.01, theshold_in_months=36)
		spousal_err.early_retirement_benefit_reduction_piece_set.create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)

		survivor_err = EarlyRetirementBenefitReduction.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), 
			benefit_type=EarlyRetirementBenefitReduction.SURVIVOR)
		survivor_err.survivor_early_retirement_benefit_reduction_piece_set.create(max_percentage_reduction=0.285)

		spouse_insurance_benefit = SpousalInsuranceBenefit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)

		gpo = GovernmentPensionOffset.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)

		drc = DelayRetirementCredit.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
		DelayRetirementCreditPiece.objects.create(inital_percentage=0.08, min_year=1943, max_year=MAX_POSITIVE_INTEGER, percentage_rate=0, year_change=1, delay_retirement_credit=drc)

		wep = WindfallEliminationProvision.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))

		aime = AverageIndexedMonthlyEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_years_for_highest_indexed_earnings=35)

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

		max_tax_amount = Money.objects.create(amount=Decimal(118500))
		MaximumTaxableEarning.objects.create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_money=max_tax_amount)

		BenefitRule.objects.create(
			start_date=date(2016,1,1),
			end_date=date(2016,12,31),
			earliest_retirement_age_law=era, 
			normal_retirement_age_law=nra,
			aime_law=aime,
			pia_law=pia,
			wep_pia_law=wep_pia, 
			wep_law=wep, 
			drc_law=drc, 
			primary_err_law=err, 
			gpo_law=gpo,
			spousal_insurance_benefit_law=spouse_insurance_benefit,
			survivor_insurance_benefit_law=survivor_insurance_benefit) 

	def test_get_updated_partial_record(self):
		beneficary = Person.objects.create(year_of_birth=1954, retirement_age=66)
		spouse = Person.objects.create(year_of_birth=1954, retirement_age=66)

		relationship = Relationship(
			person1=beneficary, 
			person2=spouse, 
			person1_role=Relationship.BENEFICIARY,
			person2_role=Relationship.SPOUSE,
			relationship_type=Relationship.MARRIED)
		relationship.save()

		beneficary_record = Record(
			person=beneficary,
			basic_primary_insurance_amount=Money.objects.create(amount=839.00),
			monthly_non_covered_pension=Money.objects.create(amount=1595.00),
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=Money.objects.create(amount=428.00))
		beneficary_record.save()

		spouse_record = Record(
			person=spouse,
			basic_primary_insurance_amount=Money.objects.create(amount=1829.00),
			monthly_non_covered_pension=Money.objects.create(amount=0.00),
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=Money.objects.create(amount=0.00))
		spouse_record.save()

		url = reverse('benefit-rule:person-get-updated-record', args=[beneficary.id])
		payload = {
			'config': {
					'partial_update': True,
					'non_covered_earning_available': False,
					'covered_earning_available': False
			}
		}
		self.assertEqual(Record.objects.count(), 2)

		response = self.client.post(url, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Record.objects.count(), 2)

		beneficiary_record = Record.objects.get(person=beneficary)
		self.assertAlmostEqual(beneficiary_record.basic_primary_insurance_amount, Money(amount=Decimal(839.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.monthly_non_covered_pension, Money(amount=Decimal(1595.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.wep_reduction, Money(amount=Decimal(428.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.final_primary_insurance_amount, Money(amount=Decimal(411.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.delay_retirement_credit, 0.00, places=2) #
		self.assertAlmostEqual(beneficiary_record.early_retirement_reduction, 0.00, places=2) #
		self.assertAlmostEqual(beneficiary_record.benefit, Money(amount=Decimal(411.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.government_pension_offset, Money(amount=Decimal(1063.33)), places=2)
		self.assertAlmostEqual(beneficiary_record.spousal_insurance_benefit, Money(amount=Decimal(0.00)), places=2)
		self.assertAlmostEqual(beneficiary_record.survivor_insurance_benefit, Money(amount=Decimal(354.67)), places=2)

		factory = APIRequestFactory()
		request = factory.post(url, payload, format='json')
		serializer = RecordSerializer(beneficiary_record, context={'request': request})
		self.assertEqual(response.data, serializer.data)

	def test_get_updated_detail_partial_record(self):
		beneficary = Person.objects.create(year_of_birth=1954, retirement_age=66)
		spouse = Person.objects.create(year_of_birth=1954, retirement_age=66)

		relationship = Relationship(
			person1=beneficary, 
			person2=spouse, 
			person1_role=Relationship.BENEFICIARY,
			person2_role=Relationship.SPOUSE,
			relationship_type=Relationship.MARRIED)
		relationship.save()

		beneficary_record = Record(
			person=beneficary,
			basic_primary_insurance_amount=Money.objects.create(amount=839.00),
			monthly_non_covered_pension=Money.objects.create(amount=1595.00),
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=Money.objects.create(amount=428.00),

			final_primary_insurance_amount=Money.objects.create(amount=Decimal(411.00)),
			benefit=Money.objects.create(amount=Decimal(411.00)),
			government_pension_offset=Money.objects.create(amount=Decimal(1063.33)),
			spousal_insurance_benefit=Money.objects.create(amount=Decimal(0.00)),
			survivor_insurance_benefit=Money.objects.create(amount=Decimal(354.67)))
		beneficary_record.save()

		spouse_record = Record(
			person=spouse,
			basic_primary_insurance_amount=Money.objects.create(amount=1829.00),
			monthly_non_covered_pension=Money.objects.create(amount=0.00),
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=Money.objects.create(amount=0.00))
		spouse_record.save()

		url = reverse('benefit-rule:person-get-updated-detail-record', args=[beneficary.id])
		payload = {
			'config': {
					'partial_update': True,
					'non_covered_earning_available': False,
					'covered_earning_available': False
			}
		}
		self.assertEqual(Record.objects.count(), 2)
		self.assertEqual(DetailRecord.objects.count(), 0)

		response = self.client.post(url, payload, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(Record.objects.count(), 2)
		self.assertEqual(DetailRecord.objects.count(), 2)

		beneficiary_detail_record = DetailRecord.objects.get(person=beneficary)
		# self.assertGreaterEqual(beneficiary_detail_record.basic_primary_insurance_amount_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.monthly_non_covered_pension_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.wep_reduction_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.final_primary_insurance_amount_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.delay_retirement_credit_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.early_retirement_reduction_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.benefit_task.instruction_set.count(), 1)
		self.assertGreaterEqual(beneficiary_detail_record.government_pension_offset_task.instruction_set.count(), 1)
		self.assertGreaterEqual(beneficiary_detail_record.spousal_insurance_benefit_task.instruction_set.count(), 1)
		# self.assertGreaterEqual(beneficiary_detail_record.survivor_insurance_benefit_task.instruction_set.count(), 1) # not implemented yet

		factory = APIRequestFactory()
		request = factory.post(url, payload, format='json')
		serializer = DetailRecordSerializer(beneficiary_detail_record, context={'request': request})
		self.assertEqual(response.data, serializer.data)