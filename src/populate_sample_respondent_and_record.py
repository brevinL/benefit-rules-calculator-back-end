import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import Relationship
from NEOandNDEBenefitCalculator.models import Money, Respondent
from rest_framework.reverse import reverse

# Start execution here!
if __name__ == '__main__':
	print("Starting Respondent & Record population script...")

	m1 = Money.objects.get_or_create(amount=30000.00)
	m2 = Money.objects.create(amount=40000.00)
	m3 = Money.objects.create(amount=50000.00)
	m4 = Money.objects.create(amount=0.00)

	beneficary, created = Respondent.objects.get_or_create(
		year_of_birth=1954,
		years_of_covered_earnings=15,
		annual_covered_earning=m1,
		years_of_non_covered_earnings=25,
		annual_non_covered_earning=m2,
		fraction_of_non_covered_aime_to_non_covered_pension=0.67,
		early_retirement_reduction=0.00,
		delay_retirement_credit=0.00,
		spousal_early_retirement_reduction=0.00,
		survivor_early_retirement_reduction=0.00)

	spouse, created = Respondent.objects.get_or_create(
		year_of_birth=1954,
		years_of_covered_earnings=40,
		annual_covered_earning=m3,
		years_of_non_covered_earnings=0,
		annual_non_covered_earning=m4,
		fraction_of_non_covered_aime_to_non_covered_pension=0.67,
		early_retirement_reduction=0.00,
		delay_retirement_credit=0.00,
		spousal_early_retirement_reduction=0.00,
		survivor_early_retirement_reduction=0.00)

	try:
		relationship = Relationship.objects.get(
			person1=beneficary, 
			person2=spouse, 
			person1_role=Relationship.BENEFICIARY,
			person2_role=Relationship.SPOUSE,
			relationship_type=Relationship.MARRIED)
	except Relationship.DoesNotExist:
		relationship = Relationship(
			content_object1=beneficary, 
			content_object2=spouse, 
			person1_role=Relationship.BENEFICIARY,
			person2_role=Relationship.SPOUSE,
			relationship_type=Relationship.MARRIED)
		relationship.save()

	import argparse
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--record', action='store_true',
		help='create record for sample respondent and spouse')
	parser.add_argument('--detail-record', action='store_true',
		help='create detail record for sample respondent and spouse')
	args = parser.parse_args()
	args = vars(args)

	import urllib.request
	domain = 'localhost:8000'

	if(args['record'] or not(args['record'] and args['detail_record'])):
		path = reverse('neo-and-nde-benefit-calculator:respondent-detail', args=[beneficary.id])
		action = 'get_updated_record/'
		url = f"http://{domain}{path}{action}"
		print(url)
		contents = urllib.request.urlopen(url).read()
		print(contents)

	if(args['detail_record'] or not(args['record'] and args['detail_record'])):
		path = reverse('neo-and-nde-benefit-calculator:respondent-detail', args=[beneficary.id])
		action = 'get_updated_detail_record/'
		url = f"http://{domain}{path}{action}"
		print(url)
		contents = urllib.request.urlopen(url).read()
		print(contents)

	print("Finish Respondent & Record population script.")