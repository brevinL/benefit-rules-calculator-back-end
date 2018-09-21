from django.db import models
from .Money import Money
from .Utilities import ordinal
from .Instruction import Task

# https://www.ssa.gov/oact/cola/Benefits.html
# https://www.ssa.gov/oact/progdata/retirebenefit1.html
class AverageIndexedMonthlyEarning(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	max_years_for_highest_indexed_earnings = models.IntegerField()

	# https://obliviousinvestor.com/how-social-security-benefits-are-calculated/
	def calculate(self, taxable_earnings): # test against []
		if not taxable_earnings:
			return Money(amount=0)
		highest_indexed_earnings = sorted(taxable_earnings, reverse=True)[:self.max_years_for_highest_indexed_earnings]
		average_indexed_yearly_earning = sum(highest_indexed_earnings) / self.max_years_for_highest_indexed_earnings
		average_indexed_monthly_earning = average_indexed_yearly_earning / 12
		return average_indexed_monthly_earning

	def stepByStep(self, taxable_earnings):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description='Get indexed yearly earnings', order=1)
		instruction.expression_set.create(description=f'indexed yearly earnings = {", ".join([str(x) for x in taxable_earnings])}', order=1)

		sorted_taxable_earnings = sorted(taxable_earnings)
		instruction = task.instruction_set.create(description=f'Sort indexed yearly earnings in descending order', order=2)
		instruction.expression_set.create(description=f'indexed yearly earnings = {", ".join([str(x) for x in sorted_taxable_earnings])}', order=1)

		highest_indexed_earnings = sorted_taxable_earnings[:self.max_years_for_highest_indexed_earnings]
		instruction = task.instruction_set.create(description=f'Get highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings', order=3)
		instruction.expression_set.create(description=f'highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings = {", ".join([str(x) for x in highest_indexed_earnings])}', order=1)

		average_indexed_yearly_earning = sum(highest_indexed_earnings) / self.max_years_for_highest_indexed_earnings
		instruction = task.instruction_set.create(description='Get average indexed yearly earning', order=4)
		instruction.expression_set.create(description=f'average indexed yearly earning = ' \
			f'sum of highest {self.max_years_for_highest_indexed_earnings} indexed yearly earnings ' \
			'/ number of highest indexed yearly earnings', order=1)
		instruction.expression_set.create(description=f'average indexed yearly earning = {sum(highest_indexed_earnings)} / {self.max_years_for_highest_indexed_earnings}', order=2)
		instruction.expression_set.create(description=f'average indexed yearly earning = {average_indexed_yearly_earning}', order=3)

		instruction = task.instruction_set.create(description='Divide average indexed yearly earning by 12', order=5)
		instruction.expression_set.create(description='average indexed monthly earning = average indexed yearly earning / 12', order=1)
		instruction.expression_set.create(description=f'average indexed monthly earning = {average_indexed_yearly_earning} / 12', order=2)
		instruction.expression_set.create(description=f'average indexed monthly earning = {average_indexed_yearly_earning / 12}', order=3)

		return task