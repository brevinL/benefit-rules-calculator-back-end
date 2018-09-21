from fractions import Fraction
from django.db import models
from .Instruction import Task

# https://www.ssa.gov/planners/retire/gpo.html

# The GPO reduces the amount of your Social Security spouse's, widow's, or widower's benefits 
# two-thirds of the amount of your government pension. 
# For example, if you receive a monthly civil service pension of $600, 
# two-thirds of that, or $400, must be used to offset your Social Security spouse's, 
# widow's, or widower's benefits. If you are eligible for a $500 spouse's benefit, 
# you will receive $100 per month from Social Security ($500 - $400 = $100).
class GovernmentPensionOffset(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	offset = models.FloatField()

	def calculate(self, monthly_non_covered_pension):
		return monthly_non_covered_pension * self.offset

	def stepByStep(self, monthly_non_covered_pension):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description='Get monthly non covered pension', order=1)
		instruction.expression_set.create(description=f'monthly non covered pension = {monthly_non_covered_pension}', order=1)

		instruction = task.instruction_set.create(description='Get offset', order=2)
		instruction.expression_set.create(description=f'offset = {Fraction(self.offset).limit_denominator()}', order=1)

		instruction = task.instruction_set.create(description='Multiply the monthly non covered pension with the offset', order=3)
		instruction.expression_set.create(description='government pension offset = monthly non covered pension x offset', order=1)
		instruction.expression_set.create(description=f'government pension offset = {monthly_non_covered_pension} x {Fraction(self.offset).limit_denominator()}', order=2)
		instruction.expression_set.create(description=f'government pension offset = {monthly_non_covered_pension * self.offset}', order=3)

		return task