from django.db import models

class Person(models.Model):
	year_of_birth = models.PositiveIntegerField(null=True)
	retirement_age = models.PositiveIntegerField(null=True)

	@property
	def year_of_retirement(self):
		return self.year_of_birth + self.retirement_age