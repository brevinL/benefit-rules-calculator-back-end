from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

# generic relationship
class Relationship(models.Model):
	# https://stackoverflow.com/questions/6335986/how-can-i-restrict-djangos-genericforeignkey-to-a-list-of-models
	# https://stackoverflow.com/questions/42838030/django-is-it-possible-to-limit-contenttype-by-base-parent
	limit = {'model__in': ['person', 'respondent']}

	content_type1 = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='content_type1')
	object_id1 = models.PositiveIntegerField()
	content_object1 = GenericForeignKey('content_type1', 'object_id1')

	content_type2 = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='content_type2')
	object_id2 = models.PositiveIntegerField()
	content_object2 = GenericForeignKey('content_type2', 'object_id2')

	HUSBAND = 'Husband'
	WIFE = 'Wife'
	BENEFICIARY = 'Beneficiary'
	SPOUSE = 'Spouse' 
	ROLE_TYPE_CHOICES = (
		(HUSBAND, 'Husband'),
		(WIFE, 'Wife'),
		(BENEFICIARY, 'Beneficiary'),
		(SPOUSE, 'Spouse')

	)
	person1_role = models.CharField(
		max_length=50,
		choices=ROLE_TYPE_CHOICES,
		null=True
	)
	person2_role = models.CharField(
		max_length=50,
		choices=ROLE_TYPE_CHOICES,
		null=True
	)
	MARRIED = 'M'
	RELATIONSHIP_TYPE_CHOICES = (
		(MARRIED, 'Married'),
	)
	relationship_type = models.CharField(
		max_length=1,
		choices=RELATIONSHIP_TYPE_CHOICES,
		null=True
	)
	start_date = models.DateField(null=True, blank=True)
	end_date = models.DateField(null=True, blank=True)

	class Meta:
		unique_together = ('content_type1', 'content_type2', 'object_id1', 'object_id2')

	def get_other(self, content_object):
		if content_object == self.content_object1:
			return self.content_object2
		else:
			return self.content_object1