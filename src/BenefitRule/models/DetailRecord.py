from django.db import models
from django.db.models import Max
from .Instruction import Task
from .Utilities import percentage
from .Earning import Earning
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class DetailRecordConfig(object):
	partial_update = False
	non_covered_earning_available = True
	covered_earning_available = True

	def __init__(self, obj={}):
		self.partial_update = obj.get('partial_update', self.partial_update)
		self.non_covered_earning_available = obj.get('non_covered_earning_available', self.non_covered_earning_available)
		self.covered_earning_available = obj.get('covered_earning_available', self.covered_earning_available)

# todo: inherit from record for polymorphism
class DetailRecord(models.Model):
	limit = {'model__in': ['person', 'respondent']}
	
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	average_indexed_monthly_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning_task") 
	basic_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount_task") 
	wep_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount_task") 
	average_indexed_monthly_non_covered_earning_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning_task") 
	wep_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="wep_reduction_task") 
	final_primary_insurance_amount_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount_task")
	delay_retirement_credit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="delay_retirement_credit_task")
	early_retirement_reduction_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="early_retirement_reduction_task")
	benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="benefit_task") 
	government_pension_offset_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="government_pension_offset_task")
	monthly_non_covered_pension_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension_task") 
	spousal_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit_task") 
	survivor_insurance_benefit_task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit_task") 

	config = DetailRecordConfig()

	class Meta:
		unique_together = ('content_type', 'object_id')

	def calculate_annual_covered_earnings(self, earnings):
		if earnings is None:
			return None
		annual_covered_earnings = earnings.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY)
		return annual_covered_earnings

	def create_average_indexed_monthly_covered_earning_task(self, aime_law, taxable_earnings):
		if taxable_earnings is None:
			return None
		return aime_law.stepByStep(taxable_earnings=taxable_earnings)

	def create_basic_primary_insurance_amount_task(self, pia_law, average_indexed_monthly_earning, year_of_coverage=0):
		if average_indexed_monthly_earning is None or year_of_coverage is None:
			return None
		return pia_law.stepByStep(
			average_indexed_monthly_earning=average_indexed_monthly_earning, 
			year_of_coverage=year_of_coverage)

	def create_wep_primary_insurance_amount_task(self, wep_pia_law, average_indexed_monthly_earning, year_of_coverage):
		if average_indexed_monthly_earning is None or year_of_coverage is None:
			return None
		return wep_pia_law.stepByStep(
			average_indexed_monthly_earning=average_indexed_monthly_earning,
			year_of_coverage=year_of_coverage)

	def calculate_annual_non_covered_earnings(self, earnings):
		if earnings is None:
			return None
		annual_non_covered_earnings = earnings.filter(type_of_earning=Earning.NONCOVERED, time_period=Earning.YEARLY)
		return annual_non_covered_earnings

	def create_average_indexed_monthly_non_covered_earning_task(self, aime_law, taxable_earnings):
		if taxable_earnings is None:
			return None
		return aime_law.stepByStep(taxable_earnings=taxable_earnings)

	def create_government_pension_offset_task(self, gpo_law, monthly_non_covered_pension):
		if monthly_non_covered_pension is None:
			return None
		return gpo_law.stepByStep(monthly_non_covered_pension=monthly_non_covered_pension)

	def create_wep_reduction_task(self, wep_law, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		if primary_insurance_amount is None or wep_primary_insurance_amount is None or monthly_non_covered_pension is None:
			return None
		return wep_law.stepByStep(
			primary_insurance_amount=primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			monthly_non_covered_pension=monthly_non_covered_pension)

	def create_final_primary_insurance_amount_task(self, basic_primary_insurance_amount, wep_reduction, final_primary_insurance_amount):
		if basic_primary_insurance_amount is None or wep_reduction is None or final_primary_insurance_amount is None:
			return None
		final_primary_insurance_amount_task = Task.objects.create()
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get primary insurance amount', order=1)
		instruction.expression_set.create(description=f'primary insurance amount = {basic_primary_insurance_amount}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Get windfall elimination provision amount', order=2)
		instruction.expression_set.create(description=f'windfall elimination provision amount = {wep_reduction}', order=1)
		instruction = final_primary_insurance_amount_task.instruction_set.create(description='Recalculate primary insurance amount by reducing the primary insurance amount with the windfall elimination provision amount', order=3)
		instruction.expression_set.create(description='primary insurance amount  = primary insurance amount - windfall elimination provision', order=1)
		instruction.expression_set.create(description=f'primary insurance amount  = {basic_primary_insurance_amount} - {wep_reduction}', order=2)
		instruction.expression_set.create(description=f'primary insurance amount = {final_primary_insurance_amount}', order=3)

		return final_primary_insurance_amount_task

	def create_delay_retirement_credit_task(self, drc_law, year_of_birth, normal_retirement_age, max_delay_retirement_credit, delay_retirement_credit):
		if year_of_birth is None or normal_retirement_age is None or max_delay_retirement_credit is None or delay_retirement_credit is None:
			return None
		delay_retirement_credit_task = drc_law.stepByStep(
			year_of_birth=year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			delayed_retirement_age=drc_law.age_limit)
		return delay_retirement_credit_task

	def create_early_retirement_reduction_task(self, primary_err_law, normal_retirement_age, earliest_retirement_age, max_early_retirement_reduction, early_retirement_reduction):
		if normal_retirement_age is None or earliest_retirement_age is None or max_early_retirement_reduction is None or early_retirement_reduction is None:
			return None
		early_retirement_reduction_task = primary_err_law.stepByStep(normal_retirement_age=normal_retirement_age, 
			early_retirement_age=earliest_retirement_age)
		return early_retirement_reduction_task

	def create_benefit_task(self, delay_retirement_credit, early_retirement_reduction, final_primary_insurance_amount, benefit):
		if delay_retirement_credit is None or early_retirement_reduction is None or final_primary_insurance_amount is None or benefit is None:
			return None
		benefit_task = Task.objects.create()
		instruction = benefit_task.instruction_set.create(description='Get delay retirement credit', order=1)
		instruction.expression_set.create(description=f'delay retirement credit = {percentage(delay_retirement_credit)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get early retirement reduction', order=2)
		instruction.expression_set.create(description=f'early retirement reduction = {percentage(early_retirement_reduction)}', order=1)
		instruction = benefit_task.instruction_set.create(description='Get primary insurance amount', order=3)
		instruction.expression_set.create(description=f'primary insurance amount = {final_primary_insurance_amount}', order=1)
		instruction = benefit_task.instruction_set.create(description='Calculate benefit', order=4)
		instruction.expression_set.create(description='benefit = primary insurance amount x (1 + (delay retirement credit + early retirement reduction))', order=1)
		instruction.expression_set.create(description=f'benefit = {final_primary_insurance_amount} x (1 + ({percentage(delay_retirement_credit)} + {percentage(early_retirement_reduction)}))', order=2)
		instruction.expression_set.create(description=f'benefit = {final_primary_insurance_amount} x {percentage(1 + (delay_retirement_credit + early_retirement_reduction))}', order=3)
		instruction.expression_set.create(description=f'benefit = {benefit}', order=3)

		return benefit_task

	def calculate_retirement_record(self, benefit_rules, beneficiary_record, config=None):
		config = self.config if config is None else config

		if config.covered_earning_available:
			annual_covered_earnings = self.calculate_annual_covered_earnings(earnings=self.content_object.earnings)
		else:
			annual_covered_earnings = None

		if self.average_indexed_monthly_covered_earning_task is None or not config.partial_update: 
			self.average_indexed_monthly_covered_earning_task = self.create_average_indexed_monthly_covered_earning_task(
				aime_law=benefit_rules.aime_law,
				taxable_earnings=annual_covered_earnings)

		if self.basic_primary_insurance_amount_task is None or not config.partial_update:
			self.basic_primary_insurance_amount_task = self.create_basic_primary_insurance_amount_task(
				pia_law=benefit_rules.pia_law,
				average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning)

		if annual_covered_earnings is None or not config.partial_update:
			years_of_annual_covered_earnings = None
		else:
			years_of_annual_covered_earnings = annual_covered_earnings.count()

		if self.wep_primary_insurance_amount_task is None or not config.partial_update:
			self.wep_primary_insurance_amount_task = self.create_wep_primary_insurance_amount_task(
				wep_pia_law=benefit_rules.wep_pia_law,
				average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning,
				year_of_coverage=years_of_annual_covered_earnings)

		if config.non_covered_earning_available:
			annual_non_covered_earnings = self.calculate_annual_non_covered_earnings(earnings=self.content_object.earnings)
		else:
			annual_non_covered_earnings = None

		if self.average_indexed_monthly_covered_earning_task is None or not config.partial_update:
			self.average_indexed_monthly_non_covered_earning_task = self.create_average_indexed_monthly_non_covered_earning_task(
				aime_law=benefit_rules.aime_law,
				taxable_earnings=annual_non_covered_earnings)

		if self.government_pension_offset_task is None or not config.partial_update:
			self.government_pension_offset_task = self.create_government_pension_offset_task(
				gpo_law=benefit_rules.gpo_law, 
				monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)

		if self.wep_reduction_task is None or not config.partial_update:
			self.wep_reduction_task = self.create_wep_reduction_task(
				wep_law=benefit_rules.wep_law,
				primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
				wep_primary_insurance_amount=beneficiary_record.wep_primary_insurance_amount,
				monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)

		if self.final_primary_insurance_amount_task is None or not config.partial_update:
			self.final_primary_insurance_amount_task = self.create_final_primary_insurance_amount_task(
				basic_primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount,
				wep_reduction=beneficiary_record.wep_reduction,
				final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount)

		if self.delay_retirement_credit_task is None or not config.partial_update:
			self.delay_retirement_credit_task = self.create_delay_retirement_credit_task(
				drc_law=benefit_rules.drc_law,
				year_of_birth=self.content_object.year_of_birth, 
				normal_retirement_age=beneficiary_record.normal_retirement_age, 
				max_delay_retirement_credit=beneficiary_record.max_delay_retirement_credit,
				delay_retirement_credit=beneficiary_record.delay_retirement_credit)

		if self.early_retirement_reduction_task is None or not config.partial_update:
			self.early_retirement_reduction_task = self.create_early_retirement_reduction_task(
				primary_err_law=benefit_rules.primary_err_law,
				normal_retirement_age=beneficiary_record.normal_retirement_age,
				earliest_retirement_age=beneficiary_record.earliest_retirement_age,
				max_early_retirement_reduction=beneficiary_record.max_early_retirement_reduction,
				early_retirement_reduction=beneficiary_record.early_retirement_reduction)

		if self.benefit_task is None or not config.partial_update:
			self.benefit_task = self.create_benefit_task(
				delay_retirement_credit=beneficiary_record.delay_retirement_credit, 
				early_retirement_reduction=beneficiary_record.early_retirement_reduction, 
				final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount, 
				benefit=beneficiary_record.benefit)

		self.save()
		return self

	def calculate_spousal_insurance_benefit(self, spousal_insurance_benefit_law, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		if primary_insurance_amount is None or spousal_primary_insurance_amount is None or government_pension_offset is None:
			return None
		spousal_insurance_benefit_task = spousal_insurance_benefit_law.stepByStep(
			primary_insurance_amount=primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_primary_insurance_amount,
			government_pension_offset=government_pension_offset)
		spousal_insurance_benefit_task.save()
		return spousal_insurance_benefit_task
		
	def calculate_dependent_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		if self.spousal_insurance_benefit_task is None or not config.partial_update:
			self.spousal_insurance_benefit_task = self.calculate_spousal_insurance_benefit(
				spousal_insurance_benefit_law=benefit_rules.spousal_insurance_benefit_law,
				primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
				spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
				government_pension_offset=beneficiary_record.government_pension_offset)
			self.save()
		return self

	def calculate_survivor_insurance_benefit(self, survivor_insurance_benefit_law, primary_insurance_amount, deceased_spousal_primary_insurance_amount, 
		survivor_early_retirement_reduction_factor, spousal_delay_retirement_factor, government_pension_offset):
		if primary_insurance_amount is None or deceased_spousal_primary_insurance_amount is None or survivor_early_retirement_reduction_factor is None or \
			spousal_delay_retirement_factor is None or government_pension_offset is None:
			return None
		survivor_insurance_benefit = survivor_insurance_benefit_law.calculate(
			primary_insurance_amount=primary_insurance_amount, 
			deceased_spousal_primary_insurance_amount=deceased_spousal_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=survivor_early_retirement_reduction_factor, 
			spousal_delay_retirement_factor=spousal_delay_retirement_factor,
			government_pension_offset=government_pension_offset)
		survivor_insurance_benefit.save()
		return survivor_insurance_benefit

	def calculate_survivor_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		if self.survivor_insurance_benefit_task is None or not config.partial_update:
			self.survivor_insurance_benefit_task = self.calculate_survivor_insurance_benefit(
				survivor_insurance_benefit_law=benefit_rules.survivor_insurance_benefit_law,
				primary_insurance_amount=beneficiary_record.benefit, 
				deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
				survivor_early_retirement_reduction_factor=beneficiary_record.survivor_early_retirement_reduction, 
				spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
				government_pension_offset=beneficiary_record.government_pension_offset)
			self.save()
		return self	