from math import isinf
from django.db import models

# https://www.ssa.gov/oact/progdata/nra.html
class RetirementAge(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()

	EARLIEST = 'E'
	NORMAL = 'N'
	LATEST = 'D'
	RETIREMENT_TYPE_CHOICES = (
		(EARLIEST, 'Earliest'),
		(NORMAL, 'Normal'),
		(LATEST, 'Latest')
	)
	retirement_type = models.CharField(
		max_length=1,
		choices=RETIREMENT_TYPE_CHOICES,
		default=NORMAL,
	)

	def calculate(self, year_of_birth):
		piece = self.retirement_age_pieces.get(start_year__lte=year_of_birth, end_year__gte=year_of_birth)
		return piece.calculate(year_of_birth)

class RetirementAgePiece(models.Model):
	initial_retirement_age = models.FloatField() # year, month
	start_year = models.IntegerField()
	end_year = models.IntegerField()
	normal_retirement_age_change = models.FloatField() # year, month
	year_of_birth_change = models.IntegerField() # should it be year and month??
	retirement_age = models.ForeignKey(RetirementAge, on_delete=models.CASCADE, related_name="retirement_age_pieces")

	def calculate(self, year_of_birth):
		if(not(self.start_year <= year_of_birth and self.end_year >= year_of_birth)):
			raise ValueError(f'year_of_birth: {self.year_of_birth} is not with in range, start_year: {self.start_year}, end_year: {self.end_year}.')

		if(isinf(self.start_year) and not isinf(self.end_year)):
			return self.initial_retirement_age + (self.end_year - year_of_birth) * ( self.normal_retirement_age_change / self.year_of_birth_change ) 
		elif(not isinf(self.start_year)):
			return self.initial_retirement_age + (year_of_birth - self.start_year) * ( self.normal_retirement_age_change / self.year_of_birth_change ) 
		elif(self.normal_retirement_age_change / self.year_of_birth_change == 0):
			return self.initial_retirement_age