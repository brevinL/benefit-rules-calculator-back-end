import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BenefitCalculator.settings')
django.setup()
from BenefitRule.models import Relationship, Person, Money, Record
from rest_framework.reverse import reverse

# Start execution here!
if __name__ == '__main__':
	print("Starting Respondent & Record population script...")

	m1= Money.objects.create(amount=30000.00)
	m2 = Money.objects.create(amount=40000.00)
	m3 = Money.objects.create(amount=50000.00)
	m4 = Money.objects.create(amount=0.00)

	beneficary = Person.objects.create(year_of_birth=1954)
	spouse = Person.objects.create(year_of_birth=1954)

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

	m1, created = Money.objects.get_or_create(amount=1595.00)
	m2, created = Money.objects.get_or_create(amount=411.00)

	# try:
	# 	record = self.record_class.objects.get(person=person)
	# except self.record_class.DoesNotExist:
	# 	record = self.record_class(content_object=person)
	# 	record.save()

	try:
		record = Record.objects.get(
			person=beneficary,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			monthly_non_covered_pension=m1,
			final_primary_insurance_amount=m2
		)
	except Record.DoesNotExist:
		record = Record(
			content_object=beneficary,
			early_retirement_reduction=0.00,
			delay_retirement_credit=0.00,
			monthly_non_covered_pension=m1,
			final_primary_insurance_amount=m2
		)
		record.save()

	import urllib.request
	domain = 'localhost:8000'

	path = reverse('benefit-rule:person-get-updated-record', args=[beneficary.id])
	url = f"http://{domain}{path}"
	print(url)
	contents = urllib.request.urlopen(url).read()
	print(contents)

	print("Finish Respondent & Record population script.")