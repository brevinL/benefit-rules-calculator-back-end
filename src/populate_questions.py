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
		key='basic_primary_insurance_amount',
		value='',
		label='Primary Insurance Amount',
		required=True,
		order=1,
		min=0)
	Question.objects.get_or_create(
		benefit_rule=Question.GPO, 
		controlType=Question.currency, 
		key='monthly_non_covered_pension',
		value='',
		label='Monthly Non-Covered Pension',
		required=True,
		order=1,
		min=0)

def populate_windfall_elimination_pension_questions():
	Question.objects.get_or_create(
		benefit_rule=Question.WEP, 
		controlType=Question.currency, 
		key='basic_primary_insurance_amount',
		value='',
		label='Primary Insurance Amount',
		required=True,
		order=1,
		min=0)
	Question.objects.get_or_create(
		benefit_rule=Question.WEP, 
		controlType=Question.currency, 
		key='monthly_non_covered_pension',
		value='',
		label='Monthly Non-Covered Pension',
		required=True,
		order=1,
		min=0)
	Question.objects.get_or_create(
		benefit_rule=Question.WEP, 
		controlType=Question.currency, 
		key='windfall_elimination_pension_primary_insurance_amount',
		value='',
		label='Windfall Elimination Pension\'s Primary Insurance Amount',
		required=True,
		order=1,
		min=0)


# Start execution here!
if __name__ == '__main__':
	print("Starting Question population script...")

	populate_government_pension_offset_questions()
	populate_windfall_elimination_pension_questions()

	print("Finish Question population script.")

