from math import isinf, inf, floor
from django.db import models
from .Money import Money
from .Utilities import ordinal, MIN_POSITIVE_INTEGER, MAX_POSITIVE_INTEGER
from .Instruction import Task

# https://www.ssa.gov/oact/cola/piaformula.html
# https://www.ssa.gov/oact/cola/bendpoints.html
'''
For 2018 these portions are the first $895, the amount between $895 and $5,397, and the amount over $5,397. 
These dollar amounts are the "bend points" of the 2018 PIA formula. 
A table shows bend points, for years beginning with 1979, for both the PIA and maximum family benefit formulas.

bendpoints != portions
'''
class PrimaryInsuranceAmount(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()

	WEP = 'W'
	BASIC = 'B'
	TYPE_OF_PRIMARY_INSURANCE_FORUMLA_CHOICES = (
		(WEP, "Windfall Elimination Provision's Primary Insurance Forumla"),
		(BASIC, 'Basic Primary Insurance Forumla')
	)
	type_of_primary_insurance_formula = models.CharField(
		max_length=1,
		choices=TYPE_OF_PRIMARY_INSURANCE_FORUMLA_CHOICES,
	)

	def calculate(self, average_indexed_monthly_earning, year_of_coverage):
		bendpoints = self.bendpoints.order_by('order')
		factors = self.factors.order_by('order')

		primary_insurance_amount = Money(amount=0)
		for index, factor in enumerate(factors):
			min_dollar = bendpoints[index].min_dollar_amount
			max_dollar = bendpoints[index].max_dollar_amount

			if isinf(min_dollar):
				min_dollar = Money(amount=0)
			elif isinf(max_dollar):
				max_dollar = Money(amount=0)

			primary_insurance_amount += max(Money(amount=0), factor.calculate(year_of_coverage) * (min(average_indexed_monthly_earning, max_dollar) - min_dollar))
			
		return floor(primary_insurance_amount * 10) / 10

	def stepByStep(self, average_indexed_monthly_earning, year_of_coverage):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description=f'Get average indexed monthly earning', order=1)
		instruction.expression_set.create(description=f'average indexed monthly earning = {average_indexed_monthly_earning}', order=1)

		bendpoints = self.bendpoints.order_by('order')
		factors = self.factors.order_by('order')

		primary_insurance_amount = Money(amount=0)
		instruction = task.instruction_set.create(description=f'Initalize total primary insurance amount to 0', order=2)
		instruction.expression_set.create(description=f'primary insurance amount = {primary_insurance_amount}', order=1)

		for index, factor in enumerate(factors):
			min_dollar = Money(amount=bendpoints[index].min_dollar_amount)
			max_dollar = Money(amount=bendpoints[index].max_dollar_amount)

			if MIN_POSITIVE_INTEGER >= min_dollar.amount and not MAX_POSITIVE_INTEGER <= max_dollar.amount:
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning up to {max_dollar} to ' \
					f'total primary insurance amount'
			elif not MIN_POSITIVE_INTEGER >= min_dollar.amount and MAX_POSITIVE_INTEGER <= max_dollar.amount:
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning above {min_dollar} to ' \
					f'total primary insurance amount'
			elif not (MIN_POSITIVE_INTEGER >= min_dollar.amount and MAX_POSITIVE_INTEGER <= max_dollar.amount):
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent his/her ' \
					f'average indexed monthly earning between {min_dollar} and ' \
					f'{max_dollar} to total primary insurance amount'
			elif MIN_POSITIVE_INTEGER >= min_dollar.amount and MAX_POSITIVE_INTEGER <= max_dollar.amount:
				description = f'Add {factor.calculate(year_of_coverage) * 100} percent of all his/her ' \
					f'average indexed monthly earning to total primary insurance amount'
			else:
				description = ''

			instruction = task.instruction_set.create(description=description, order=index + 3)

			if MIN_POSITIVE_INTEGER >= min_dollar.amount:
				min_dollar = Money(amount=0)
			elif MAX_POSITIVE_INTEGER <= max_dollar.amount:
				max_dollar = Money(amount=0)

			instruction.expression_set.create(description=f'primary insurance amount = ' \
				f'primary insurance amount + ' \
				f'max($0.00, factor x ( min(average indexed monthly earning, ' \
				'minimum dollar amount threshold) - maximum dollar amount threshold ))', order=1)
			instruction.expression_set.create(description=f'primary insurance amount = max($0.00, {primary_insurance_amount} + ' \
				f'{factor.calculate(year_of_coverage)} x ' \
				f'( min({average_indexed_monthly_earning}, {max_dollar}) - {min_dollar} ))', order=2)

			primary_insurance_amount += max(0, factor.calculate(year_of_coverage) * (min(average_indexed_monthly_earning, max_dollar.amount) - min_dollar.amount))

			instruction.expression_set.create(description=f'primary insurance amount = {primary_insurance_amount}', order=3)

		instruction = task.instruction_set.create(description=f'Round total primary insurance amount to the next lower multiple of $0.10 ' \
			'if it is not already a multiple of $0.10', order=len(factors) + 3)
		instruction.expression_set.create(description=f'primary insurance amount = floor(primary insurance amount * 10) / 10', order=1)
		instruction.expression_set.create(description=f'primary insurance amount = floor({primary_insurance_amount} * 10) / 10', order=2)
		instruction.expression_set.create(description=f'primary insurance amount = {floor(primary_insurance_amount * 10) / 10}', order=3)
		
		return task

class BendPoint(models.Model):
	min_dollar_amount = models.PositiveIntegerField() # TODO: foreign key to Money model
	max_dollar_amount = models.PositiveIntegerField() # TODO: foreign key to Money model
	order = models.PositiveIntegerField()
	primary_insurance_amount = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, related_name="bendpoints", null=True)

	class Meta:
		ordering  = ['order']

# https://www.ssa.gov/oact/cola/piaformula.html
# https://secure.ssa.gov/poms.nsf/lnx/0300605362
class Factor(models.Model):
	order = models.IntegerField()
	primary_insurance_amount = models.ForeignKey(PrimaryInsuranceAmount, on_delete=models.CASCADE, related_name="factors", null=True)

	def calculate(self, year_of_coverage):
		piece = self.factor_pieces.get(min_year_of_coverage__lte=year_of_coverage, max_year_of_coverage__gte=year_of_coverage)
		return piece.calculate(year_of_coverage)

class FactorPiece(models.Model):
	inital_factor = models.FloatField()
	min_year_of_coverage = models.PositiveIntegerField()
	max_year_of_coverage = models.PositiveIntegerField()
	year_of_coverage_change = models.IntegerField()
	factor_change = models.FloatField()
	order = models.PositiveIntegerField()
	factor = models.ForeignKey(Factor, on_delete=models.CASCADE, related_name="factor_pieces", null=True)

	def calculate(self, year_of_coverage):
		if(not(self.min_year_of_coverage <= year_of_coverage and self.max_year_of_coverage >= year_of_coverage)):
			raise ValueError(f'year_of_coverage: {year_of_coverage} is not with in range ({self.min_year_of_coverage} to {self.max_year_of_coverage}; inclusive)')

		if(isinf(self.min_year_of_coverage) and not isinf(self.max_year_of_coverage)):
			return (self.inital_factor + (self.max_year_of_coverage - year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) 
		elif(not isinf(self.min_year_of_coverage)):
			return (self.inital_factor + (year_of_coverage - self.min_year_of_coverage) * ( self.factor_change / self.year_of_coverage_change )) 
		elif(self.factor_change / self.year_of_coverage_change == 0):
			return self.inital_factor 