import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from django.contrib.contenttypes.models import ContentType
from BenefitRule.models import Relationship, Person, Money, Record
from rest_framework.reverse import reverse

# Start execution here!
if __name__ == '__main__':
	print("Starting Respondent & Record population script...")

	beneficary = Person.objects.create(year_of_birth=1954, retirement_age=66)
	spouse = Person.objects.create(year_of_birth=1954, retirement_age=66)

	person_type = ContentType.objects.get_for_model(beneficary)

	try:
		relationship = Relationship.objects.get(
			content_type1__pk=person_type.id, 
			object_id1=beneficary.id,
			content_type2__pk=person_type.id, 
			object_id2=spouse.id,
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

	m1= Money.objects.create(amount=1595.00)
	m2 = Money.objects.create(amount=411.00)
	m3 = Money.objects.create(amount=839.00)
	m4 = Money.objects.create(amount=1829.00)
	m5 = Money.objects.create(amount=0.00)
	m6 = Money.objects.create(amount=428.00)
	try:
		Record.objects.get(
			content_type__pk=person_type.id, 
			object_id=beneficary.id,
			basic_primary_insurance_amount=m3,
			monthly_non_covered_pension=m1,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=m6)
	except Record.DoesNotExist:
		record = Record(
			content_object=beneficary,
			basic_primary_insurance_amount=m3,
			monthly_non_covered_pension=m1,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=m6)
		record.save()

	try:
		Record.objects.get(
			content_type__pk=person_type.id, 
			object_id=spouse.id,
			basic_primary_insurance_amount=m4,
			monthly_non_covered_pension=m5,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=m5)
	except Record.DoesNotExist:
		record = Record(
			content_object=spouse,
			basic_primary_insurance_amount=m4,
			monthly_non_covered_pension=m5,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			wep_reduction=m5)
		record.save()

	import requests
	import json

	domain = 'localhost:8000'

	path = reverse('benefit-rule:person-get-updated-record', args=[beneficary.id])
	url = f"http://{domain}{path}"
	print(f'url: {url}')
	payload = {
		'config': {
			'partial_update': True,
			'non_covered_earning_available': False,
			'covered_earning_available': False
		}
	}
	print(f'payload: {payload}')
	r = requests.post(url, json=payload)
	print(f'headers: {r.headers}')
	print(f'content: {r.text}')

	print("Finish Respondent & Record population script.")