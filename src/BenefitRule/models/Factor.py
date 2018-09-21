from django.db import models
from math import isinf, inf 

# https://www.ssa.gov/oact/cola/piaformula.html
# https://secure.ssa.gov/poms.nsf/lnx/0300605362
class FactorPiece(models.Model):
	inital_factor = models.IntegerField()
	# https://stackoverflow.com/questions/10539026/how-to-create-a-django-floatfield-with-maximum-and-minimum-limits
	min_year_of_coverage = models.PositiveIntegerField()
	max_year_of_coverage = models.PositiveIntegerField()
	year_of_coverage_change = models.IntegerField()
	factor_change = models.IntegerField()
	order = models.IntegerField()

	def calculate(self, year_of_coverage):
		if(not(self.min_year_of_coverage <= year_of_coverage and self.max_year_of_coverage >= year_of_coverage)):
			raise ValueError(f'year_of_coverage: {year_of_coverage} is not with in range, min_year_of_coverage: {self.min_year_of_coverage}, max_year_of_coverage: {self.max_year_of_coverage}.')

		if(isinf(self.min_year_of_coverage) and not isinf(self.max_year_of_coverage)):
			return (self.inital_factor + (self.max_year_of_coverage - year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) / 100
		elif(not isinf(self.min_year_of_coverage)):
			return (self.inital_factor + (year_of_coverage - self.min_year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) / 100
		elif(self.factor_change / self.year_of_coverage_change == 0):
			return self.inital_factor / 100

class Factor(models.Model):
	factor_pieces = models.ManyToManyField(FactorPiece)
	order = models.IntegerField()

	def calculate(self, year_of_coverage):
		piece = self.factor_pieces.get(min_year_of_coverage__lte=year_of_coverage, max_year_of_coverage__gte=year_of_coverage)
		return piece.calculate(year_of_coverage)