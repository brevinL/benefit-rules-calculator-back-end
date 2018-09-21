from django.db import models
from .ERR import EarlyRetirementBenefitReduction
from .Money import Money 

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
		pass