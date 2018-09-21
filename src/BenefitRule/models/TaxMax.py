from django.db import models
from .Earning import Earning
from .Money import Money

# https://www.ssa.gov/planners/maxtax.html
class MaximumTaxableEarning(models.Model): # should be foregin key to money to get the decimal amount
	start_date = models.DateField()
	end_date = models.DateField()
	
	# amount = models.IntegerField()
	max_money = models.ForeignKey(Money, on_delete=models.CASCADE)

	def calculate(self, earning):
		return min(earning.money, self.max_money) # should it be returning earning to be consistent?