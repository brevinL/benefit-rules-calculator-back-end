from django.db import models
from .Money import Money
from .Instruction import Task

# https://secure.ssa.gov/poms.nsf/lnx/0300605362
# https://www.ssa.gov/planners/retire/wep-chart.html
# https://www.ssa.gov/planners/retire/anyPiaWepjs04.html
'''
The Windfall Elimination Provision (WEP) reduces your Eligibility Year (ELY) benefit amount 
before it is reduced or increased due to early retirement, delayed retirement credits, 
cost-of-living adjustments (COLA), or other factors.
'''
class WindfallEliminationProvision(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	# why not have pia as a parameter rather than a one to one?
	def calculate(self, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		# the total WEP reduction is limited to one-half of the pension based on the earnings that were not covered by Social Security
		return min(monthly_non_covered_pension * 1/2, primary_insurance_amount - wep_primary_insurance_amount)

	def stepByStep(self, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		task = Task.objects.create()
		
		instruction = task.instruction_set.create(description="Get WEP's primary insurance amount", order=1)
		instruction.expression_set.create(description="WEP's primary insurance amount = primary insurance amount", order=1)
		instruction.expression_set.create(description=f"WEP's primary insurance amount = {wep_primary_insurance_amount}", order=2)

		instruction = task.instruction_set.create(description="Get monthly non covered pension", order=2)
		instruction.expression_set.create(description=f"monthly non covered pension = {monthly_non_covered_pension}", order=1)

		instruction = task.instruction_set.create(description="Get primary insurance amount", order=3)
		instruction.expression_set.create(description=f"primary insurance amount = {primary_insurance_amount}", order=1)

		wep_reduction = min(monthly_non_covered_pension * 1/2, max(primary_insurance_amount - wep_primary_insurance_amount, 0))

		instruction = task.instruction_set.create(description='Find Windfall Elimination Provision reduction', order=4)
		instruction.expression_set.create(description='WEP reduction = min(monthly non covered pension x 1/2, max(primary insurance amount - WEP\'s primary insurance amount, 0))', order=1)
		instruction.expression_set.create(description=f'WEP reduction = min({monthly_non_covered_pension} x 1/2, max({primary_insurance_amount} - {wep_primary_insurance_amount}, 0))', order=2)
		instruction.expression_set.create(description=f'WEP reduction = min({monthly_non_covered_pension * 1/2}, max({primary_insurance_amount - wep_primary_insurance_amount}, 0)', order=3)
		instruction.expression_set.create(description=f'WEP reduction = min({monthly_non_covered_pension * 1/2}, {max(primary_insurance_amount - wep_primary_insurance_amount, 0)})', order=4)
		instruction.expression_set.create(description=f'WEP reduction = {wep_reduction}', order=5)

		return task