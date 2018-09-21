from datetime import date
from math import inf, floor
from django.test import TestCase
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from BenefitRule.models import SurvivorInsuranceBenefit, Money, ordinal, currency

class SurvivorInsuranceBenefitTestCase(TestCase):
	def setUp(self):
		SurvivorInsuranceBenefit.objects.create(start_date=date.min, end_date=date.max, max_benefit_entitlement_factor=0.825)

	def test_calculate_without_max_survivor_benefit_reduction(self):
		survivor_insurance_benefit = SurvivorInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) &
			Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(354.00, survivor_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			deceased_spousal_primary_insurance_amount=Money(amount=1829), 
			survivor_early_retirement_reduction_factor=0,
			spousal_delay_retirement_factor=0, 
			government_pension_offset=Money(amount=1064))
		)

	def test_calculate_with_max_suvivor_benefit_reduction(self):
		survivor_insurance_benefit = SurvivorInsuranceBenefit.objects.get(
			Q(start_date__lte=date(2016, 1, 1)) &
			Q(end_date__gte=date(2016, 12, 31))
		)
		self.assertAlmostEqual(33.92, survivor_insurance_benefit.calculate(
			primary_insurance_amount=Money(amount=411), 
			deceased_spousal_primary_insurance_amount=Money(amount=1829),
			survivor_early_retirement_reduction_factor=0.285,
			spousal_delay_retirement_factor=0, 
			government_pension_offset=Money(amount=1064)), places=2)