from fractions import Fraction
from django.db import models
from .Money import Money
from .Instruction import Task

# https://www.ssa.gov/planners/retire/applying6.html
# https://www.ssa.gov/oact/quickcalc/spouse.html
# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.03/handbook-0305.html
class SpousalInsuranceBenefit(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	max_benefit_entitlement_factor = models.FloatField()

	# how to check if they applied for their own benefits?
	# case: applied but resulted in 0 due to wep cut vs didnt applied
	def isEntitled(self, primary_insurance_amount, spousal_primary_insurance_amount):
		return primary_insurance_amount < self.maxEntitlement(spousal_primary_insurance_amount)

	def maxEntitlement(self, spousal_primary_insurance_amount):
		return spousal_primary_insurance_amount * self.max_benefit_entitlement_factor

	# If a spouse is eligible for a retirement benefit based on his or her own earnings, 
	# and if that benefit is higher than the spousal benefit, 
	# then we pay the retirement benefit. Otherwise we pay the spousal benefit.
	def calculate(self, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		if(self.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount)): # test against money of 0 not 0
			return max(Money(amount=0), self.maxEntitlement(spousal_primary_insurance_amount) - primary_insurance_amount - government_pension_offset)
		else: # to be tested
			return Money(amount=0)

	def stepByStep(self, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description='Get spousal\' primary insurance amount', order=1)
		instruction.expression_set.create(description=f'spousal\'s primary insurance amount = {spousal_primary_insurance_amount}', order=1)

		instruction = task.instruction_set.create(description='Calculate the maximum entitlement to spousal insurance benefit', order=2)
		instruction.expression_set.create(description='maximum benefit entitlement = spousal\'s primary insurance amount x maximum benefit entitlement factor', order=1)
		instruction.expression_set.create(description=f'maximum benefit entitlement = {spousal_primary_insurance_amount} x {Fraction(self.max_benefit_entitlement_factor).limit_denominator()}', order=2)
		instruction.expression_set.create(description=f'maximum benefit entitlement = {spousal_primary_insurance_amount * self.max_benefit_entitlement_factor}', order=3)

		instruction = task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description=f'primary insurance amount = {primary_insurance_amount}', order=1)

		instruction = task.instruction_set.create(description='Determine if person is entitled to spousal insurance benefit', order=4)
		instruction.expression_set.create(description='primary insurance amount < maximum benefit entitlement?', order=1)
		instruction.expression_set.create(description=f'{primary_insurance_amount} < {self.maxEntitlement(spousal_primary_insurance_amount)}?', order=2)
		instruction.expression_set.create(description=f'{primary_insurance_amount < self.maxEntitlement(spousal_primary_insurance_amount)}', order=3)

		if(not self.isEntitled(primary_insurance_amount, spousal_primary_insurance_amount)):
			instruction = task.instruction_set.create(description='Set spousal insurance benefit to zero', order=5)
			instruction.expression_set.create(description=f'spousal insurance benefit = {Money(amount=0)}', order=1)
			return task

		spousal_insurance_benefit = self.maxEntitlement(spousal_primary_insurance_amount)

		instruction = task.instruction_set.create(description='Set spousal insurance benefit to maximum benefit entitlement', order=5)
		instruction.expression_set.create(description='spousal insurance benefit = maximum benefit entitlement', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = {spousal_insurance_benefit}', order=2)
		
		instruction = task.instruction_set.create(description='Subtract the primary insurance amount from spousal insurance benefit', order=6)
		instruction.expression_set.create(description='spousal insurance benefit = spousal insurance benefit - primary insurance amount', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = {spousal_insurance_benefit} - {primary_insurance_amount}', order=2)
		instruction.expression_set.create(description=f'spousal insurance benefit = {spousal_insurance_benefit - primary_insurance_amount}', order=3)

		spousal_insurance_benefit -= primary_insurance_amount

		instruction = task.instruction_set.create(description='Get government pension offset', order=7)
		instruction.expression_set.create(description=f'government pension offset = {government_pension_offset}', order=1)

		instruction = task.instruction_set.create(description='Subtract the government pension offset from spousal insurance benefit', order=8)
		instruction.expression_set.create(description='spousal insurance benefit = spousal insurance benefit - government pension offset', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = {spousal_insurance_benefit} - {government_pension_offset}', order=2)
		instruction.expression_set.create(description=f'spousal insurance benefit = {spousal_insurance_benefit - government_pension_offset}', order=3)

		spousal_insurance_benefit -= government_pension_offset

		instruction = task.instruction_set.create(description='Cap spousal insurance benefit', order=9)
		instruction.expression_set.create(description='spousal insurance benefit = max($0.00, spousal insurance benefit)', order=1)
		instruction.expression_set.create(description=f'spousal insurance benefit = max($0.00, {spousal_insurance_benefit})', order=2)
		instruction.expression_set.create(description=f'spousal insurance benefit = {max(Money(amount=0), spousal_insurance_benefit)}', order=3)

		return task