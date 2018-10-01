from django.db import models
from .ERR import EarlyRetirementBenefitReduction
from .Money import Money 
from .Instruction import Task

# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.07/handbook-0724.html
class SurvivorInsuranceBenefit(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	max_benefit_entitlement_factor = models.FloatField()

	def calculateSurvivorEarlyRetirementReductionFactor(self, normal_retirement_age, retirement_age):
		year_of_early_retirement = min(0, normal_retirement_age - retirement_age)
		if year_of_early_retirement > 0:
			return max_benefit_entitlement_factor /  year_of_early_retirement * 12
		return 0

	def maxEntitlement(self, spousal_primary_insurance_amount):
		return spousal_primary_insurance_amount * self.max_benefit_entitlement_factor

	# check(?) if spouse is deceased
	def calculate(self, primary_insurance_amount, deceased_spousal_primary_insurance_amount, 
		survivor_early_retirement_reduction_factor, spousal_delay_retirement_factor, government_pension_offset):
		max_entitlement = self.maxEntitlement(deceased_spousal_primary_insurance_amount)
		entitlement = max(max_entitlement,  deceased_spousal_primary_insurance_amount * (1 - survivor_early_retirement_reduction_factor + spousal_delay_retirement_factor))
		return max(Money(amount=0), entitlement - primary_insurance_amount - government_pension_offset) # test: never go negative

	def stepByStep(self, primary_insurance_amount, deceased_spousal_primary_insurance_amount, 
		survivor_early_retirement_reduction_factor, spousal_delay_retirement_factor, government_pension_offset):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description='Get spousal\'s primary insurance amount', order=1)
		instruction.expression_set.create(description=f'spousal\'s primary insurance amount = {deceased_spousal_primary_insurance_amount}', order=1)

		instruction = task.instruction_set.create(description='Get max benefit enetitlement factor', order=2)
		instruction.expression_set.create(description=f'max benefit enetitlement factor = {self.max_benefit_entitlement_factor}', order=1)

		max_entitlement = self.maxEntitlement(deceased_spousal_primary_insurance_amount)
		instruction = task.instruction_set.create(description='Get max entitlement', order=3)
		instruction.expression_set.create(description=f'max entitlement = spousal\'s primary insurance amount x max benefit enetitlement factor', order=1)
		instruction.expression_set.create(description=f'max entitlement = {deceased_spousal_primary_insurance_amount} x {self.max_benefit_entitlement_factor}', order=2)
		instruction.expression_set.create(description=f'max entitlement = {max_entitlement}', order=3)

		instruction = task.instruction_set.create(description='Get survivor\'s early retirement reduction factor', order=4)
		instruction.expression_set.create(description=f'survivor\'s early retirement reduction factor = {survivor_early_retirement_reduction_factor}', order=1)

		instruction = task.instruction_set.create(description='Get spousal\'s delay retirement factor', order=5)
		instruction.expression_set.create(description=f'spousal\'s delay retirement factor = {spousal_delay_retirement_factor}', order=1)

		entitlement = deceased_spousal_primary_insurance_amount * 1 - survivor_early_retirement_reduction_factor + spousal_delay_retirement_factor
		instruction = task.instruction_set.create(description='Calculate survivor insurance benefit entitlement', order=6)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = spousal\'s primary insurance amount x (1 - survivor\'s early retirement reduction factor + spousal\'s delay retirement factor)', order=1)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {deceased_spousal_primary_insurance_amount} x (1 - {survivor_early_retirement_reduction_factor} + {spousal_delay_retirement_factor})', order=2)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {deceased_spousal_primary_insurance_amount} x ({1 - survivor_early_retirement_reduction_factor + spousal_delay_retirement_factor})', order=3)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {entitlement})', order=4)

		instruction = task.instruction_set.create(description='Cap survivor\'s insurance benefit entitlement with max entitlement', order=7)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = max(max entitlement, survivor\'s insurance benefit entitlement)', order=1)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = max({max_entitlement}, {entitlement})', order=2)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {max(max_entitlement, entitlement)}', order=3)
		entitlement = max(max_entitlement, entitlement)

		instruction = task.instruction_set.create(description='Adjust survivor\'s insurance benefit entitlement with survivor\'s primary insurance amount', order=8)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = survivor\'s insurance benefit entitlement - survivor\'s primary insurance amount', order=1)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {entitlement} - {primary_insurance_amount}', order=2)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {entitlement - primary_insurance_amount}', order=3)
		entitlement -= primary_insurance_amount

		instruction = task.instruction_set.create(description='Adjust survivor\'s insurance benefit entitlement with government pension offset', order=9)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = survivor\'s insurance benefit entitlement - government pension offset', order=1)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {entitlement} - {government_pension_offset}', order=2)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {entitlement - government_pension_offset}', order=3)
		entitlement -= government_pension_offset

		instruction = task.instruction_set.create(description='Cap survivor\'s insurance benefit entitlement to $0.00', order=9)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = max({Money(amount=0.00)}, survivor\'s insurance benefit entitlement)', order=1)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = max({Money(amount=0.00)}, {entitlement})', order=2)
		instruction.expression_set.create(description=f'survivor\'s insurance benefit entitlement = {max(Money(amount=0.00), entitlement)}', order=3)

		return task