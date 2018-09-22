from django.db import models
from .Money import Money
from .Earning import Earning
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

class Record(models.Model):
	limit = {'model__in': ['person', 'respondent']}
	
	content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit)
	object_id = models.PositiveIntegerField()
	content_object = GenericForeignKey('content_type', 'object_id')

	earliest_retirement_age = models.PositiveSmallIntegerField(null=True)
	normal_retirement_age = models.PositiveSmallIntegerField(null=True)
	average_indexed_monthly_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_covered_earning") 
	basic_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="basic_primary_insurance_amount") 
	wep_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="wep_primary_insurance_amount") 
	average_indexed_monthly_non_covered_earning = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="average_indexed_monthly_non_covered_earning") 
	monthly_non_covered_pension = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="monthly_non_covered_pension") 
	wep_reduction = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="wep_reduction") 
	final_primary_insurance_amount = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="final_primary_insurance_amount")
	max_delay_retirement_credit = models.FloatField(null=True)
	delay_retirement_credit = models.FloatField(null=True)
	max_early_retirement_reduction = models.FloatField(null=True)
	early_retirement_reduction = models.FloatField(null=True)
	benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="benefit") 
	government_pension_offset = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="government_pension_offset")
	spousal_insurance_benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="spousal_insurance_benefit") 
	survivor_insurance_benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit") 

	class Meta:
		unique_together = ('content_type', 'object_id')

	def calculate_earliest_retirement_age(self, earliest_retirement_age_law, year_of_birth):
		if year_of_birth is None:
			return None
		earliest_retirement_age = earliest_retirement_age_law.calculate(year_of_birth=year_of_birth)
		return earliest_retirement_age

	def calculate_normal_retirement_age(self, normal_retirement_age_law, year_of_birth):
		if year_of_birth is None:
			return None
		normal_retirement_age = normal_retirement_age_law.calculate(year_of_birth=year_of_birth)
		return normal_retirement_age

	def calculate_annual_covered_earnings(self, earnings):
		if earnings is None:
			return None
		annual_covered_earnings = earnings.filter(type_of_earning=Earning.COVERED, time_period=Earning.YEARLY)
		return annual_covered_earnings

	def calculate_average_indexed_monthly_covered_earning(self, aime_law, taxable_earnings):
		if taxable_earnings is None:
			return None
		average_indexed_monthly_covered_earning = aime_law.calculate(taxable_earnings=taxable_earnings) 
		average_indexed_monthly_covered_earning.save()
		return average_indexed_monthly_covered_earning

	def calculate_basic_primary_insurance_amount(self, pia_law, average_indexed_monthly_earning, year_of_coverage=0):
		if average_indexed_monthly_earning is None or year_of_coverage is None:
			return None
		basic_primary_insurance_amount = pia_law.calculate(
			average_indexed_monthly_earning=average_indexed_monthly_earning, 
			year_of_coverage=year_of_coverage)
		basic_primary_insurance_amount.save()
		return basic_primary_insurance_amount

	def calculate_wep_primary_insurance_amount(self, wep_pia_law, average_indexed_monthly_earning, year_of_coverage):
		if average_indexed_monthly_earning is None or year_of_coverage is None:
			return None
		wep_primary_insurance_amount = wep_pia_law.calculate(
			average_indexed_monthly_earning=average_indexed_monthly_earning,
			year_of_coverage=year_of_coverage)
		wep_primary_insurance_amount.save()
		return wep_primary_insurance_amount

	def calculate_annual_non_covered_earnings(self, earnings):
		if earnings is None:
			return None
		annual_non_covered_earnings = earnings.filter(type_of_earning=Earning.NONCOVERED, time_period=Earning.YEARLY)
		return annual_non_covered_earnings

	def calculate_average_indexed_monthly_non_covered_earning(self, aime_law, taxable_earnings):
		if taxable_earnings is None:
			return None
		average_indexed_monthly_non_covered_earning = aime_law.calculate(taxable_earnings=taxable_earnings) 
		average_indexed_monthly_non_covered_earning.save()
		return average_indexed_monthly_non_covered_earning

	def calculate_government_pension_offset(self, gpo_law, monthly_non_covered_pension):
		if monthly_non_covered_pension is None:
			return None
		government_pension_offset = gpo_law.calculate(monthly_non_covered_pension=monthly_non_covered_pension)
		government_pension_offset.save()
		return government_pension_offset

	def calculate_wep_reduction(self, wep_law, primary_insurance_amount, wep_primary_insurance_amount, monthly_non_covered_pension):
		if primary_insurance_amount is None or wep_primary_insurance_amount is None or monthly_non_covered_pension is None:
			return None
		wep_reduction = wep_law.calculate(
			primary_insurance_amount=primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			monthly_non_covered_pension=monthly_non_covered_pension)
		wep_reduction.save()
		return wep_reduction

	def calculate_final_primary_insurance_amount(self, basic_primary_insurance_amount, wep_reduction):
		if basic_primary_insurance_amount is None or wep_reduction is None:
			return None
		final_primary_insurance_amount = basic_primary_insurance_amount - wep_reduction
		final_primary_insurance_amount.save()
		return final_primary_insurance_amount

	def calculate_max_delay_retirement_credit(self, drc_law, year_of_birth, normal_retirement_age):
		if year_of_birth is None or normal_retirement_age is None:
			return None
		max_delay_retirement_credit = drc_law.calculate(
			year_of_birth=year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			delayed_retirement_age=drc_law.age_limit)
		return max_delay_retirement_credit

	def calculate_delay_retirement_credit(self, drc_law, year_of_birth, normal_retirement_age, retirement_age, max_delay_retirement_credit):
		if year_of_birth is None or normal_retirement_age is None or retirement_age is None or max_delay_retirement_credit is None:
			return None
		delay_retirement_credit = drc_law.calculate(
			year_of_birth=year_of_birth,
			normal_retirement_age=normal_retirement_age,
			delayed_retirement_age=retirement_age)
		delay_retirement_credit = min(max_delay_retirement_credit, delay_retirement_credit) #
		return delay_retirement_credit

	def calculate_max_early_retirement_reduction(self, primary_err_law, normal_retirement_age, earliest_retirement_age):
		if normal_retirement_age is None or earliest_retirement_age is None:
			return None
		max_early_retirement_reduction = primary_err_law.calculate(
			normal_retirement_age=normal_retirement_age, 
			early_retirement_age=earliest_retirement_age)
		return max_early_retirement_reduction

	def calculate_early_retirement_reduction(self, primary_err_law, normal_retirement_age, retirement_age, max_early_retirement_reduction):
		if normal_retirement_age is None or retirement_age is None or max_early_retirement_reduction is None:
			return None
		early_retirement_reduction = primary_err_law.calculate(
			normal_retirement_age=normal_retirement_age, 
			early_retirement_age=retirement_age)
		early_retirement_reduction = min(max_early_retirement_reduction, early_retirement_reduction) #
		return early_retirement_reduction

	def calculate_benefit(self, final_primary_insurance_amount, delay_retirement_credit, early_retirement_reduction):
		if final_primary_insurance_amount is None or delay_retirement_credit is None or early_retirement_reduction is None:
			return None
		benefit = final_primary_insurance_amount * (1 + (delay_retirement_credit - early_retirement_reduction))
		benefit.save()
		return benefit

	def calculate_retirement_record(self, benefit_rules):
		earliest_retirement_age = self.calculate_earliest_retirement_age(
			earliest_retirement_age_law=benefit_rules.earliest_retirement_age_law,
			year_of_birth=self.content_object.year_of_birth)
		normal_retirement_age = self.calculate_normal_retirement_age(
			normal_retirement_age_law=benefit_rules.normal_retirement_age_law,
			year_of_birth=self.content_object.year_of_birth)
		annual_covered_earnings = self.calculate_annual_covered_earnings(earnings=self.content_object.earning_set)
		average_indexed_monthly_covered_earning = self.calculate_average_indexed_monthly_covered_earning(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=annual_covered_earnings) 
		basic_primary_insurance_amount = self.calculate_basic_primary_insurance_amount(
			pia_law=benefit_rules.pia_law,
			average_indexed_monthly_earning=average_indexed_monthly_covered_earning)
		wep_primary_insurance_amount = self.calculate_wep_primary_insurance_amount(
			wep_pia_law=benefit_rules.wep_pia_law, 
			average_indexed_monthly_earning=average_indexed_monthly_covered_earning,
			year_of_coverage=annual_covered_earnings.count())
		annual_non_covered_earnings = self.calculate_annual_non_covered_earnings(earnings=self.content_object.earning_set)
		average_indexed_monthly_non_covered_earning = self.calculate_average_indexed_monthly_non_covered_earning(
			aime_law=benefit_rules.aime_law, 
			taxable_earnings=annual_non_covered_earnings)
		# monthly_non_covered_pension = average_indexed_monthly_non_covered_earning * respondent.fraction_of_non_covered_aime_to_non_covered_pension
		government_pension_offset = self.calculate_government_pension_offset(
			gpo_law=benefit_rules.gpo_law, 
			monthly_non_covered_pension=monthly_non_covered_pension)
		wep_reduction = self.calculate_wep_reduction(
			wep_law=benefit_rules.wep_law, 
			primary_insurance_amount=basic_primary_insurance_amount, 
			wep_primary_insurance_amount=wep_primary_insurance_amount, 
			monthly_non_covered_pension=monthly_non_covered_pension)
		final_primary_insurance_amount = self.calculate_final_primary_insurance_amount(
			basic_primary_insurance_amount=basic_primary_insurance_amount, 
			wep_reduction=wep_reduction)
		max_delay_retirement_credit = self.calculate_max_delay_retirement_credit(
			drc_law=benefit_rules.drc_law, 
			year_of_birth=self.content_object.year_of_birth, 
			normal_retirement_age=normal_retirement_age)
		delay_retirement_credit = self.calculate_delay_retirement_credit(
			drc_law=benefit_rules.drc_law, 
			year_of_birth=self.content_object.year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			retirement_age=self.content_object.retirement_age,
			max_delay_retirement_credit=max_delay_retirement_credit)
		max_early_retirement_reduction = self.calculate_max_early_retirement_reduction(
			primary_err_law=benefit_rules.primary_err_law, 
			normal_retirement_age=normal_retirement_age, 
			earliest_retirement_age=earliest_retirement_age)
		early_retirement_reduction = self.calculate_early_retirement_reduction(
			primary_err_law=benefit_rules.primary_err_law, 
			normal_retirement_age=normal_retirement_age, 
			retirement_age=self.content_object.retirement_age, 
			max_early_retirement_reduction=max_early_retirement_reduction)
		benefit = self.calculate_benefit(
			final_primary_insurance_amount=final_primary_insurance_amount, 
			delay_retirement_credit=delay_retirement_credit, 
			early_retirement_reduction=early_retirement_reduction)

		return self.update_record(
			earliest_retirement_age=earliest_retirement_age,
			normal_retirement_age=normal_retirement_age,
			average_indexed_monthly_covered_earning=average_indexed_monthly_covered_earning,
			basic_primary_insurance_amount=basic_primary_insurance_amount,
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			average_indexed_monthly_non_covered_earning=average_indexed_monthly_non_covered_earning,
			monthly_non_covered_pension=monthly_non_covered_pension,
			government_pension_offset=government_pension_offset,
			wep_reduction=wep_reduction,
			final_primary_insurance_amount=final_primary_insurance_amount,
			max_delay_retirement_credit=max_delay_retirement_credit,
			delay_retirement_credit=delay_retirement_credit,
			max_early_retirement_reduction=max_early_retirement_reduction,
			early_retirement_reduction=early_retirement_reduction,
			benefit=benefit)

	def update_record(self,
		earliest_retirement_age=None,
		normal_retirement_age=None,
		average_indexed_monthly_covered_earning=None,
		basic_primary_insurance_amount=None,
		wep_primary_insurance_amount=None,
		average_indexed_monthly_non_covered_earning=None,
		monthly_non_covered_pension=None,
		government_pension_offset=None,
		wep_reduction=None,
		final_primary_insurance_amount=None,
		max_delay_retirement_credit=None,
		delay_retirement_credit=None,
		max_early_retirement_reduction=None,
		early_retirement_reduction=None,
		benefit=None):
		if not earliest_retirement_age is None:
			self.earliest_retirement_age = earliest_retirement_age
		if not normal_retirement_age is None:
			self.normal_retirement_age = normal_retirement_age
		if not average_indexed_monthly_covered_earning is None:
			self.average_indexed_monthly_covered_earning = average_indexed_monthly_covered_earning
		if not basic_primary_insurance_amount is None:
			self.basic_primary_insurance_amount = basic_primary_insurance_amount
		if not wep_primary_insurance_amount is None:
			self.wep_primary_insurance_amount = wep_primary_insurance_amount
		if not average_indexed_monthly_non_covered_earning is None:
			self.average_indexed_monthly_non_covered_earning = average_indexed_monthly_non_covered_earning
		if not monthly_non_covered_pension is None:
			self.monthly_non_covered_pension = monthly_non_covered_pension
		if not government_pension_offset is None:
			self.government_pension_offset = government_pension_offset
		if not wep_reduction is None:
			self.wep_reduction = wep_reduction
		if not final_primary_insurance_amount is None:
			self.final_primary_insurance_amount = final_primary_insurance_amount
		if not max_delay_retirement_credit is None:
			self.max_delay_retirement_credit = max_delay_retirement_credit
		if not delay_retirement_credit is None:
			self.delay_retirement_credit = delay_retirement_credit
		if not max_early_retirement_reduction is None:
			self.max_early_retirement_reduction = max_early_retirement_reduction
		if not early_retirement_reduction is None:
			self.early_retirement_reduction = early_retirement_reduction
		if not benefit is None:
			self.benefit = benefit
		self.save()
		return self

	def calculate_dependent_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		beneficiary_record.spousal_insurance_benefit = benefit_rules.spousal_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
			government_pension_offset=beneficiary_record.government_pension_offset)
		beneficiary_record.spousal_insurance_benefit.save()
		return beneficiary_record

	def calculate_survivor_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record):
		survivor_early_retirement_reduction = benefit_rules.survivor_insurance_benefit_law.calculateSurvivorEarlyRetirementReductionFactor(
			normal_retirement_age=beneficiary_record.normal_retirement_age,
			retirement_age=self.content_object.retirement_age)
		beneficiary_record.survivor_insurance_benefit = benefit_rules.survivor_insurance_benefit_law.calculate(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		beneficiary_record.survivor_insurance_benefit.save()
		return beneficiary_record