from datetime import date
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import *

def populate_normal_retirement_age_law():
	nra, created = RetirementAge.objects.get_or_create(start_date=date.min, end_date=date.max, retirement_type=RetirementAge.NORMAL)
	nra.retirement_age_pieces.get_or_create(initial_retirement_age=65, start_year=MIN_INTEGER, end_year=1937, 
		normal_retirement_age_change=0, year_of_birth_change=1)
	nra.retirement_age_pieces.get_or_create(initial_retirement_age=(65+2/12), start_year=1938, end_year=1942, 
		normal_retirement_age_change=2/12, year_of_birth_change=1)
	nra.retirement_age_pieces.get_or_create(initial_retirement_age=66, start_year=1943, end_year=1954, 
		normal_retirement_age_change=0, year_of_birth_change=1)
	nra.retirement_age_pieces.get_or_create(initial_retirement_age=(66+2/12), start_year=1955, end_year=1959, 
		normal_retirement_age_change=2/12, year_of_birth_change=1)
	nra.retirement_age_pieces.get_or_create(initial_retirement_age=67, start_year=1960, end_year=MAX_INTEGER, 
		normal_retirement_age_change=0, year_of_birth_change=1)
	return nra

def populate_early_retirement_age_law():
	era, created = RetirementAge.objects.get_or_create(start_date=date.min, end_date=date.max, retirement_type=RetirementAge.EARLIEST)
	era.retirement_age_pieces.get_or_create(initial_retirement_age=62, start_year=MIN_INTEGER, end_year=MAX_INTEGER, 
		normal_retirement_age_change=0, year_of_birth_change=1)
	return era

def populate_delay_retirement_age_law():
	dra, created = RetirementAge.objects.get_or_create(start_date=date.min, end_date=date.max, retirement_type=RetirementAge.LATEST)
	dra.retirement_age_pieces.get_or_create(initial_retirement_age=70, start_year=MIN_INTEGER, end_year=MAX_INTEGER, 
		normal_retirement_age_change=0, year_of_birth_change=1)
	return dra

def populate_spousal_insurance_benefit_law():
	spousal_insurance_benefit_law, created = SpousalInsuranceBenefit.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=1/2)
	return spousal_insurance_benefit_law

def populate_survivor_insurance_benefit_law():
	survivor_insurance_benefit_law, created = SurvivorInsuranceBenefit.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_benefit_entitlement_factor=0.825)
	return survivor_insurance_benefit_law

def populate_primary_early_retirement_benefit_reduction_law():
	err, created = EarlyRetirementBenefitReduction.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), benefit_type=EarlyRetirementBenefitReduction.PRIMARY)
	err.early_retirement_benefit_reduction_piece_set.get_or_create(factor=5/9, percentage=0.01, theshold_in_months=36)
	err.early_retirement_benefit_reduction_piece_set.get_or_create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)
	return err

def populate_spousal_early_retirement_benefit_reduction_law():
	spousal_err, created = EarlyRetirementBenefitReduction.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), benefit_type=EarlyRetirementBenefitReduction.SPOUSAL)
	spousal_err.early_retirement_benefit_reduction_piece_set.get_or_create(factor=25/36, percentage=0.01, theshold_in_months=36)
	spousal_err.early_retirement_benefit_reduction_piece_set.get_or_create(factor=5/12, percentage=0.01, theshold_in_months=MAX_POSITIVE_INTEGER)
	return spousal_err

def populate_survivor_early_retirement_benefit_reduction_law():
	survivor_err, created = EarlyRetirementBenefitReduction.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), benefit_type=EarlyRetirementBenefitReduction.SURVIVOR)
	survivor_err.survivor_early_retirement_benefit_reduction_piece_set.get_or_create(max_percentage_reduction=0.285)
	return survivor_err

def populate_government_pension_offset_law():
	government_pension_offset_law, created = GovernmentPensionOffset.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), offset=2/3)
	return government_pension_offset_law

def populate_delay_retirement_credit_law():
	drc, created = DelayRetirementCredit.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), age_limit=70)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.055, min_year=1933, max_year=1934, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.06, min_year=1935, max_year=1936, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.065, min_year=1937, max_year=1938, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.07, min_year=1939, max_year=1940, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.075, min_year=1941, max_year=1942, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	DelayRetirementCreditPiece.objects.get_or_create(inital_percentage=0.08, min_year=1943, max_year=MAX_POSITIVE_INTEGER, percentage_rate=0, year_change=1, delay_retirement_credit=drc)
	return drc

def populate_windfall_elimination_provision_law():
	windfall_elimination_provision_law, created = WindfallEliminationProvision.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31))	
	return windfall_elimination_provision_law

def populate_average_indexed_monthly_earning_law():
	average_indexed_monthly_earning_law, created = AverageIndexedMonthlyEarning.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), max_years_for_highest_indexed_earnings=35)
	return average_indexed_monthly_earning_law

def populate_basic_primary_insurance_amount_law():
	pia, created = PrimaryInsuranceAmount.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), type_of_primary_insurance_formula=PrimaryInsuranceAmount.BASIC)
	BendPoint.objects.get_or_create(min_dollar_amount=MIN_POSITIVE_INTEGER, max_dollar_amount=856, order=1, primary_insurance_amount=pia)
	BendPoint.objects.get_or_create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=pia)
	BendPoint.objects.get_or_create(min_dollar_amount=5157, max_dollar_amount=MAX_POSITIVE_INTEGER, order=3, primary_insurance_amount=pia)

	f1, created = Factor.objects.get_or_create(order=1, primary_insurance_amount=pia)
	FactorPiece.objects.get_or_create(inital_factor=0.90, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
		year_of_coverage_change=1, factor_change=0, order=1, factor=f1)

	f2, created = Factor.objects.get_or_create(order=2, primary_insurance_amount=pia)
	FactorPiece.objects.get_or_create(inital_factor=0.32, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
		year_of_coverage_change=1, factor_change=0, order=1, factor=f2)

	f3, created = Factor.objects.get_or_create(order=3, primary_insurance_amount=pia)
	FactorPiece.objects.get_or_create(inital_factor=0.15, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
		year_of_coverage_change=1, factor_change=0, order=1, factor=f3)
	return pia

def populate_wep_primary_insurance_amount_law():
	wep_pia, created = PrimaryInsuranceAmount.objects.get_or_create(start_date=date(2016, 1, 1), end_date=date(2016, 12, 31), type_of_primary_insurance_formula=PrimaryInsuranceAmount.WEP)
	BendPoint.objects.get_or_create(min_dollar_amount=MIN_POSITIVE_INTEGER, max_dollar_amount=856, order=1, primary_insurance_amount=wep_pia)
	BendPoint.objects.get_or_create(min_dollar_amount=856, max_dollar_amount=5157, order=2, primary_insurance_amount=wep_pia)
	BendPoint.objects.get_or_create(min_dollar_amount=5157, max_dollar_amount=MAX_POSITIVE_INTEGER, order=3, primary_insurance_amount=wep_pia)

	f1, created = Factor.objects.get_or_create(order=1, primary_insurance_amount=wep_pia)
	FactorPiece.objects.get_or_create(inital_factor=0.40, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=20, year_of_coverage_change=1, factor_change=0, order=1, factor=f1)
	FactorPiece.objects.get_or_create(inital_factor=0.45, min_year_of_coverage=21, max_year_of_coverage=29, year_of_coverage_change=1, factor_change=0.05, order=2, factor=f1)
	FactorPiece.objects.get_or_create(inital_factor=0.90, min_year_of_coverage=30, max_year_of_coverage=MAX_POSITIVE_INTEGER, year_of_coverage_change=1, factor_change=0, order=3, factor=f1)

	f2, created = Factor.objects.get_or_create(order=2, primary_insurance_amount=wep_pia)
	FactorPiece.objects.get_or_create(inital_factor=0.32, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
		year_of_coverage_change=1, factor_change=0, order=1, factor=f2)

	f3, created = Factor.objects.get_or_create(order=3, primary_insurance_amount=wep_pia)
	FactorPiece.objects.get_or_create(inital_factor=0.15, min_year_of_coverage=MIN_POSITIVE_INTEGER, max_year_of_coverage=MAX_POSITIVE_INTEGER, 
		year_of_coverage_change=1, factor_change=0, order=1, factor=f3)
	return wep_pia

# Start execution here!
if __name__ == '__main__':
	print("Starting Benefit Rule population script...")
	normal_retirement_age_law = populate_normal_retirement_age_law()
	early_retirement_age_law = populate_early_retirement_age_law()
	delay_retirement_age_law = populate_delay_retirement_age_law()
	spousal_insurance_benefit_law = populate_spousal_insurance_benefit_law()
	survivor_insurance_benefit_law = populate_survivor_insurance_benefit_law()
	primary_early_retirement_benefit_reduction_law = populate_primary_early_retirement_benefit_reduction_law()
	spousal_early_retirement_benefit_reduction_law = populate_spousal_early_retirement_benefit_reduction_law()
	survivor_early_retirement_benefit_reduction_law = populate_survivor_early_retirement_benefit_reduction_law()
	government_pension_offset_law = populate_government_pension_offset_law()
	delay_retirement_credit_law = populate_delay_retirement_credit_law()
	windfall_elimination_provision_law = populate_windfall_elimination_provision_law()
	average_indexed_monthly_earning_law = populate_average_indexed_monthly_earning_law()
	basic_primary_insurance_amount_law = populate_basic_primary_insurance_amount_law()
	wep_primary_insurance_amount_law = populate_wep_primary_insurance_amount_law()

	benefit_rule, create = BenefitRule.objects.get_or_create(
		start_date=date(2016, 1, 1),
		end_date=date(2016, 12, 31),
		earliest_retirement_age_law=early_retirement_age_law,
		normal_retirement_age_law=normal_retirement_age_law,
		aime_law=average_indexed_monthly_earning_law,
		pia_law=basic_primary_insurance_amount_law,
		wep_pia_law=wep_primary_insurance_amount_law,
		wep_law=windfall_elimination_provision_law,
		drc_law=delay_retirement_credit_law,
		primary_err_law=primary_early_retirement_benefit_reduction_law,
		gpo_law=government_pension_offset_law,
		spousal_insurance_benefit_law=spousal_insurance_benefit_law,
		survivor_insurance_benefit_law=survivor_insurance_benefit_law)
	# delay_retirement_age_law
	# spousal_early_retirement_benefit_reduction_law
	# survivor_early_retirement_benefit_reduction_law
	print("Finish Benefit Rule population script.")

