from django.db import models

# https://www.ssa.gov/oact/cola/QC.html
class QuarterOfCoverage(models.Model):
	# max_quarter_of_coverage_per_year = models.IntegerField()
	# person = models.ForeignKey(Person, on_delete=models.CASCADE)
	minimum_required_quarter_of_coverage = models.IntegerField()

	def isInsured(self, quarter_of_coverage):
		return self.quarter_of_coverage == self.minimum_required_quarter_of_coverage