from math import isinf
from django.db import models
from .Utilities import percentage
from .Instruction import Task

# https://www.ssa.gov/planners/retire/delayret.html
class DelayRetirementCredit(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	age_limit = models.FloatField() # year and month of an age (no infs)

	def calculate(self, year_of_birth, normal_retirement_age, delayed_retirement_age):
		normal_retirement_age = float(normal_retirement_age)
		delayed_retirement_age = float(delayed_retirement_age)
		if normal_retirement_age >= delayed_retirement_age:
			return 0
		forumla_piece = self.delay_retirement_credit_pieces.get(min_year__lte=year_of_birth, max_year__gte=year_of_birth)
		yearly_percent_rate_of_increase = forumla_piece.calculate(year_of_birth)
		return (min(self.age_limit, delayed_retirement_age) + 1 - normal_retirement_age) * yearly_percent_rate_of_increase

	def stepByStep(self, year_of_birth, normal_retirement_age, delayed_retirement_age):
		task = Task.objects.create()

		normal_retirement_age = float(normal_retirement_age)
		delayed_retirement_age = float(delayed_retirement_age)
		
		instruction = task.instruction_set.create(description='Get normal retirement age', order=1)
		instruction.expression_set.create(description=f'normal retirement age = {normal_retirement_age}', order=1)

		instruction = task.instruction_set.create(description='Get delayed retirement age', order=2)
		instruction.expression_set.create(description=f'delayed retirement age = {delayed_retirement_age}', order=1)

		instruction = task.instruction_set.create(description='Determine if person is eligible for delay retirement credit', order=3)
		instruction.expression_set.create(description='normal retirement age < delayed retirement age?', order=1)
		instruction.expression_set.create(description=f'{normal_retirement_age} < {delayed_retirement_age}?', order=2)
		instruction.expression_set.create(description=f'{normal_retirement_age < delayed_retirement_age}', order=3)

		if normal_retirement_age >= delayed_retirement_age:
			instruction = task.instruction_set.create(description='Set delay retirement benefit percentage increase to zero', order=4) 
			instruction.expression_set.create(description=f'delay retirement benefit percentage increase = {percentage(0)}', order=1)
			return task

		instruction = task.instruction_set.create(description='Get delay retirement age limit', order=4)
		instruction.expression_set.create(description=f'delay retirement age limit = {self.age_limit}', order=1)

		instruction = task.instruction_set.create(description='Capped retirement age if retirement age is greater than delay retirement age limit', order=5)
		instruction.expression_set.create(description='retirement age = min(delay retirement age limit, retirement age)', order=1)
		instruction.expression_set.create(description=f'retirement age = min({self.age_limit}, {delayed_retirement_age})', order=2)
		instruction.expression_set.create(description=f'retirement age = {min(self.age_limit, delayed_retirement_age)}', order=3)

		delayed_retirement_age = min(self.age_limit, delayed_retirement_age)

		number_of_years_delayed = delayed_retirement_age + 1 - normal_retirement_age

		instruction = task.instruction_set.create(description='Determine number of years delayed', order=6)
		instruction.expression_set.create(description='number of years delayed = retirement age + 1 - normal retirement age', order=1)
		instruction.expression_set.create(description=f'number of years delayed = {delayed_retirement_age} + 1 - {normal_retirement_age}', order=2)
		instruction.expression_set.create(description=f'number of years delayed = {delayed_retirement_age + 1 - normal_retirement_age}', order=3)

		forumla_piece = self.delay_retirement_credit_pieces.get(min_year__lte=year_of_birth, max_year__gte=year_of_birth)
		yearly_percent_rate_of_increase = forumla_piece.calculate(year_of_birth)
		delay_retirement_benefit_percentage_increase = (min(self.age_limit, delayed_retirement_age) + 1 - normal_retirement_age) * yearly_percent_rate_of_increase

		instruction = task.instruction_set.create(description='Determine number of years delayed', order=7)
		instruction.expression_set.create(description=f'delay retirement benefit percentage increase = number of years delayed * monthly percent rate of increase', order=1)
		instruction.expression_set.create(description=f'delay retirement benefit percentage increase = {number_of_years_delayed} * {percentage(yearly_percent_rate_of_increase)}', order=2)
		instruction.expression_set.create(description=f'delay retirement benefit percentage increase = {percentage(delay_retirement_benefit_percentage_increase)}', order=3)

		return task

class DelayRetirementCreditPiece(models.Model):
	inital_percentage = models.FloatField()
	min_year = models.PositiveIntegerField()
	max_year = models.PositiveIntegerField()
	percentage_rate = models.FloatField()
	year_change = models.IntegerField()
	delay_retirement_credit = models.ForeignKey(DelayRetirementCredit, 
		on_delete=models.CASCADE, related_name="delay_retirement_credit_pieces", null=True)

	def calculate(self, year_of_birth):
		if(not(self.min_year <= year_of_birth and self.max_year >= year_of_birth)):
			raise ValueError(f'year_of_birth: {year_of_birth} is not with in range, min_year: {self.min_year}, max_year: {self.max_year}.')

		if(isinf(self.min_year) and not isinf(self.max_year)):
			return self.inital_percentage + (self.max_year - year_of_birth) * ( self.percentage_rate / self.year_change )
		elif(not isinf(self.min_year)):
			return self.inital_percentage + (year_of_birth - self.min_year) * ( self.percentage_rate / self.year_change ) 
		elif(self.percentage_rate / self.year_change == 0):
			return self.inital_percentage 