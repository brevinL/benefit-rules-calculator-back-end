from datetime import date
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import Question

def populate_government_pension_offset_questions():
	Question.objects.get_or_create(
		benefit_rule=Question.GPO, 
		controlType=Question.currency, 
		key='government_pension_offset',
		value='',
		required=True,
		order=1,
		min=0)
	Question.objects.get_or_create(
		benefit_rule=Question.GPO, 
		controlType=Question.currency, 
		key='government_pension_offset',
		value='',
		required=True,
		order=1,
		min=0)

def populate_government_pension_offset_questions():

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

