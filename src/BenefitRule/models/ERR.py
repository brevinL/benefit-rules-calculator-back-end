from fractions import Fraction
from django.db import models
from .RA import RetirementAge
from .Utilities import percentage, MIN_POSITIVE_INTEGER, MAX_POSITIVE_INTEGER
from .Instruction import Task

# https://www.ssa.gov/oact/quickcalc/early_late.html
# https://www.ssa.gov/oact/quickcalc/earlyretire.html
# https://www.ssa.gov/oact/quickcalc/spouse.html
# https://www.ssa.gov/OP_Home%2Fhandbook/handbook.07/handbook-0724.html
'''
A spousal benefit is reduced 25/36 of 1% for each month before normal retirement age, up to 36 months. 
If the number of months exceeds 36, then the benefit is further reduced 5/12 of 1% per month.
'''
class EarlyRetirementBenefitReduction(models.Model):
	start_date = models.DateField()
	end_date = models.DateField()
	
	SPOUSAL = 'SP'
	PRIMARY = 'PR'
	SURVIVOR = 'SU'
	BENEFIT_TYPE_CHOICES = (
		(SPOUSAL, 'Spousal'),
		(PRIMARY, 'Primary'),
		(SURVIVOR, 'Survivor')
	)
	benefit_type = models.CharField(
		max_length=2,
		choices=BENEFIT_TYPE_CHOICES,
		default=PRIMARY,
	)

	def calculate(self, normal_retirement_age, early_retirement_age):
		if normal_retirement_age <= early_retirement_age:
			return 0
		difference_in_months = abs(early_retirement_age - normal_retirement_age) * 12
		benefit_reduction_factor = 0

		if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
			pieces = self.early_retirement_benefit_reduction_piece_set.all()
		elif self.benefit_type == self.SURVIVOR:
			pieces = self.survivor_early_retirement_benefit_reduction_piece_set.all()

		for piece in pieces:
			benefit_reduction_factor += piece.calculate(difference_in_months)
			if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
				difference_in_months -= piece.theshold_in_months

		return benefit_reduction_factor

	def stepByStep(self, normal_retirement_age, early_retirement_age):
		task = Task.objects.create()

		instruction = task.instruction_set.create(description='Get normal retirement age', order=1)
		instruction.expression_set.create(description=f'normal retirement age = {normal_retirement_age}', order=1)

		instruction = task.instruction_set.create(description='Get early retirement age', order=2)
		instruction.expression_set.create(description=f'early retirement age = {early_retirement_age}', order=1)

		instruction = task.instruction_set.create(description='Determine if person is eligible for early retirement benefit reduction', order=3)
		instruction.expression_set.create(description='normal retirement age > early retirement age?', order=1)
		instruction.expression_set.create(description=f'{normal_retirement_age} > {early_retirement_age}?', order=2)
		instruction.expression_set.create(description=f'{normal_retirement_age > early_retirement_age}', order=3)

		if normal_retirement_age <= early_retirement_age:
			instruction = task.instruction_set.create(description='Set early retirement benefit percentage reduction to zero', order=4)
			instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(0)}', order=1)
			return task

		instruction = task.instruction_set.create(description='Determine number of months before normal retirement age', order=4)
		instruction.expression_set.create(description='number of months before normal retirement age = | early retirement age - normal retirement age | * 12', order=1)
		instruction.expression_set.create(description=f'number of months before normal retirement age = | {early_retirement_age} - {normal_retirement_age} | * 12', order=2)
		instruction.expression_set.create(description=f'number of months before normal retirement age = {abs(early_retirement_age - normal_retirement_age)} * 12', order=3)
		instruction.expression_set.create(description=f'number of months before normal retirement age = {abs(early_retirement_age - normal_retirement_age) * 12}', order=4)

		difference_in_months = abs(early_retirement_age - normal_retirement_age) * 12

		instruction = task.instruction_set.create(description='Set early retirement benefit percentage reduction to zero', order=5)
		instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(0)}', order=1)

		benefit_reduction_factor = 0

		if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
			pieces = self.early_retirement_benefit_reduction_piece_set.all()
		elif self.benefit_type == self.SURVIVOR:
			pieces = self.survivor_early_retirement_benefit_reduction_piece_set.all()

		for piece in pieces:
			order = task.instruction_set.count() + 1
			if self.benefit_type == self.SPOUSAL or self.benefit_type == self.PRIMARY:
				instruction = task.instruction_set.create(description='For each month ' + \
					(f'(up to {piece.theshold_in_months} months) ' if not(piece.theshold_in_months <= MIN_POSITIVE_INTEGER or piece.theshold_in_months >= MAX_POSITIVE_INTEGER) else '') + \
					'before normal retirement age, ' \
					f'add {Fraction(piece.factor).limit_denominator()} of {percentage(piece.percentage)} to early retirement benefit percentage reduction', order=order) 
				instruction.expression_set.create(description='early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
					f'min(number of months before normal retirement age, ' + ('infinity' if piece.theshold_in_months >= MAX_POSITIVE_INTEGER else str(piece.theshold_in_months)) + ') x ' \
					f'{Fraction(piece.factor).limit_denominator()} of {percentage(piece.percentage)}', order=1)
				instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'min({difference_in_months}, ' + ('infinity' if piece.theshold_in_months >= MAX_POSITIVE_INTEGER else str(piece.theshold_in_months)) + ') x ' \
					f'{Fraction(piece.factor).limit_denominator()} x {percentage(piece.percentage)}', order=2)
				instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'{min(difference_in_months, piece.theshold_in_months)} x ' \
					f'{Fraction(piece.factor).limit_denominator()} x {percentage(piece.percentage)}', order=3)
				instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor + min(difference_in_months, piece.theshold_in_months) * piece.factor * piece.percentage)}', order=4)

				benefit_reduction_factor += piece.calculate(difference_in_months)

				if difference_in_months - piece.theshold_in_months > 0:
					instruction = task.instruction_set.create(description='Update number of months before normal retirement age', order=order + 1)
					instruction.expression_set.create(description=f'number of months before normal retirement age = {difference_in_months} - ' + ('infinity' if piece.theshold_in_months >= MAX_POSITIVE_INTEGER else str(piece.theshold_in_months)), order=1)
					instruction.expression_set.create(description=f'number of months before normal retirement age = {difference_in_months - piece.theshold_in_months}', order=2)
				difference_in_months -= piece.theshold_in_months

			if self.benefit_type == self.SURVIVOR:
				instruction = task.instruction_set.create(description='For each month before normal retirement age, ' \
					f'add {percentage(piece.factor)} to early retirement benefit percentage reduction', order=order)
				instruction.expression_set.create(description='early retirement benefit percentage reduction = early retirement benefit percentage reduction + ' \
					f'number of months before normal retirement age x {percentage(piece.factor)}', order=1)
				instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor)} + ' \
					f'{difference_in_months} x {percentage(piece.factor)}', order=2)
				instruction.expression_set.create(description=f'early retirement benefit percentage reduction = {percentage(benefit_reduction_factor + difference_in_months * piece.factor)}', order=3)
				benefit_reduction_factor += piece.factor
		return task

# critical to explain how the factors are created by writing a stepbystep in the pieces
class EarlyRetirementBenefitReductionPiece(models.Model):
	factor = models.FloatField()
	percentage = models.FloatField()
	theshold_in_months = models.PositiveIntegerField()
	early_retirement_benefit_reduction = models.ForeignKey(EarlyRetirementBenefitReduction, 
		on_delete=models.CASCADE, related_name="early_retirement_benefit_reduction_piece_set")

	def calculate(self, months):
		return self.factor * self.percentage * min(self.theshold_in_months, months)

class SurvivorEarlyRetirementBenefitReductionPiece(models.Model):
	max_percentage_reduction = models.FloatField()
	early_retirement_benefit_reduction = models.ForeignKey(EarlyRetirementBenefitReduction, 
		on_delete=models.CASCADE, related_name="survivor_early_retirement_benefit_reduction_piece_set")
	
	@property
	def factor(self):
		normal_retirement_age = RetirementAge.objects.get(
			retirement_type=RetirementAge.NORMAL,
			start_date__lte=self.early_retirement_benefit_reduction.start_date,
			end_date__gte=self.early_retirement_benefit_reduction.end_date
		).calculate(self.early_retirement_benefit_reduction.start_date.year)
		earliest_retirement_age = RetirementAge.objects.get(
			retirement_type=RetirementAge.EARLIEST,
			start_date__lte=self.early_retirement_benefit_reduction.start_date,
			end_date__gte=self.early_retirement_benefit_reduction.end_date
		).calculate(self.early_retirement_benefit_reduction.start_date.year)
		return self.max_percentage_reduction / (abs(normal_retirement_age - earliest_retirement_age + 1) * 12)

	# assumes that months is the full retirement (i.e. 62 to 66) when it shouldn't
	def calculate(self, months):
		return self.factor * months