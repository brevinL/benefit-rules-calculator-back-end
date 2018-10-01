from django.db import models
from .Money import Money
from .Earning import Earning
from .Person import Person

class RecordConfig(object):
	partial_update = False
	non_covered_earning_available = True
	covered_earning_available = True

	def __init__(self, obj={}):
		self.partial_update = obj.get('partial_update', self.partial_update)
		self.non_covered_earning_available = obj.get('non_covered_earning_available', self.non_covered_earning_available)
		self.covered_earning_available = obj.get('covered_earning_available', self.covered_earning_available)

class Record(models.Model):
	person = models.ForeignKey(Person, on_delete=models.CASCADE)
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
	survivor_early_retirement_reduction = models.FloatField(null=True)
	survivor_insurance_benefit = models.ForeignKey(Money, on_delete=models.CASCADE, null=True, related_name="survivor_insurance_benefit") 

	config = RecordConfig()

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

	def calculate_retirement_record(self, benefit_rules, config=None):
		config = self.config if config is None else config

		if self.earliest_retirement_age is None or not config.partial_update:
			self.earliest_retirement_age = self.calculate_earliest_retirement_age(
				earliest_retirement_age_law=benefit_rules.earliest_retirement_age_law,
				year_of_birth=self.person.year_of_birth)

		if self.normal_retirement_age is None or not config.partial_update:
			self.normal_retirement_age = self.calculate_normal_retirement_age(
				normal_retirement_age_law=benefit_rules.normal_retirement_age_law,
				year_of_birth=self.person.year_of_birth)

		if config.covered_earning_available:
			annual_covered_earnings = self.calculate_annual_covered_earnings(earnings=self.person.earning_set)
		else:
			annual_covered_earnings = None

		if self.average_indexed_monthly_covered_earning is None or not config.partial_update: 
			self.average_indexed_monthly_covered_earning = self.calculate_average_indexed_monthly_covered_earning(
				aime_law=benefit_rules.aime_law,
				taxable_earnings=annual_covered_earnings) 

		if self.basic_primary_insurance_amount is None or not config.partial_update:
			self.basic_primary_insurance_amount = self.calculate_basic_primary_insurance_amount(
				pia_law=benefit_rules.pia_law,
				average_indexed_monthly_earning=self.average_indexed_monthly_covered_earning)

		if annual_covered_earnings is None or not config.partial_update:
			years_of_annual_covered_earnings = None
		else:
			years_of_annual_covered_earnings = annual_covered_earnings.count()

		if self.wep_primary_insurance_amount is None or not config.partial_update:
			self.wep_primary_insurance_amount = self.calculate_wep_primary_insurance_amount(
				wep_pia_law=benefit_rules.wep_pia_law, 
				average_indexed_monthly_earning=self.average_indexed_monthly_covered_earning,
				year_of_coverage=years_of_annual_covered_earnings)

		if config.non_covered_earning_available:
			annual_non_covered_earnings = self.calculate_annual_non_covered_earnings(earnings=self.person.earning_set)
		else:
			annual_non_covered_earnings = None

		if self.average_indexed_monthly_non_covered_earning is None or not config.partial_update:
			self.average_indexed_monthly_non_covered_earning = self.calculate_average_indexed_monthly_non_covered_earning(
				aime_law=benefit_rules.aime_law, 
				taxable_earnings=annual_non_covered_earnings)

		if self.monthly_non_covered_pension is None or not config.partial_update:
			pass

		if self.government_pension_offset is None or not config.partial_update:
			self.government_pension_offset = self.calculate_government_pension_offset(
				gpo_law=benefit_rules.gpo_law, 
				monthly_non_covered_pension=self.monthly_non_covered_pension)

		if self.wep_reduction is None or not config.partial_update:
			self.wep_reduction = self.calculate_wep_reduction(
				wep_law=benefit_rules.wep_law, 
				primary_insurance_amount=self.basic_primary_insurance_amount, 
				wep_primary_insurance_amount=self.wep_primary_insurance_amount, 
				monthly_non_covered_pension=self.monthly_non_covered_pension)

		if self.final_primary_insurance_amount is None or not config.partial_update:
			self.final_primary_insurance_amount = self.calculate_final_primary_insurance_amount(
				basic_primary_insurance_amount=self.basic_primary_insurance_amount, 
				wep_reduction=self.wep_reduction) # break out wep reduction from pia

		if self.max_delay_retirement_credit is None or not config.partial_update:
			self.max_delay_retirement_credit = self.calculate_max_delay_retirement_credit(
				drc_law=benefit_rules.drc_law, 
				year_of_birth=self.person.year_of_birth, 
				normal_retirement_age=self.normal_retirement_age)

		if self.delay_retirement_credit is None or not config.partial_update:
			self.delay_retirement_credit = self.calculate_delay_retirement_credit(
				drc_law=benefit_rules.drc_law, 
				year_of_birth=self.person.year_of_birth, 
				normal_retirement_age=self.normal_retirement_age, 
				retirement_age=self.person.retirement_age,
				max_delay_retirement_credit=self.max_delay_retirement_credit)

		if self.max_early_retirement_reduction is None or not config.partial_update:
			self.max_early_retirement_reduction = self.calculate_max_early_retirement_reduction(
				primary_err_law=benefit_rules.primary_err_law, 
				normal_retirement_age=self.normal_retirement_age, 
				earliest_retirement_age=self.earliest_retirement_age)

		if self.early_retirement_reduction is None or not config.partial_update:
			self.early_retirement_reduction = self.calculate_early_retirement_reduction(
				primary_err_law=benefit_rules.primary_err_law, 
				normal_retirement_age=self.normal_retirement_age, 
				retirement_age=self.person.retirement_age, 
				max_early_retirement_reduction=self.max_early_retirement_reduction)

		if self.benefit is None or not config.partial_update:
			self.benefit = self.calculate_benefit(
				final_primary_insurance_amount=self.final_primary_insurance_amount, 
				delay_retirement_credit=self.delay_retirement_credit, 
				early_retirement_reduction=self.early_retirement_reduction) # break out drc and err from pia

		self.save()
		return self

	def calculate_spousal_insurance_benefit(self, spousal_insurance_benefit_law, primary_insurance_amount, spousal_primary_insurance_amount, government_pension_offset):
		if primary_insurance_amount is None or spousal_primary_insurance_amount is None or government_pension_offset is None:
			return None
		spousal_insurance_benefit = spousal_insurance_benefit_law.calculate(
			primary_insurance_amount=primary_insurance_amount, 
			spousal_primary_insurance_amount=spousal_primary_insurance_amount,
			government_pension_offset=government_pension_offset)
		spousal_insurance_benefit.save()
		return spousal_insurance_benefit

	def calculate_dependent_benefits(self, benefit_rules, spousal_beneficiary_record, config=None):
		config = self.config if config is None else config

		if self.spousal_insurance_benefit is None or not config.partial_update:
			self.spousal_insurance_benefit = self.calculate_spousal_insurance_benefit(
				spousal_insurance_benefit_law=benefit_rules.spousal_insurance_benefit_law,
				primary_insurance_amount=self.basic_primary_insurance_amount,
				spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount,
				government_pension_offset=self.government_pension_offset)
			self.save()
		return self

	def calculate_survivor_early_retirement_reduction(self, survivor_insurance_benefit_law, normal_retirement_age, retirement_age):
		if normal_retirement_age is None or retirement_age is None:
			return None
		survivor_early_retirement_reduction = survivor_insurance_benefit_law.calculateSurvivorEarlyRetirementReductionFactor(
			normal_retirement_age=normal_retirement_age,
			retirement_age=self.person.retirement_age)
		return survivor_early_retirement_reduction

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

	def calculate_survivor_benefits(self, benefit_rules, spousal_beneficiary_record, config=None):
		config = self.config if config is None else config

		if self.survivor_insurance_benefit is None or not config.partial_update:
			self.survivor_early_retirement_reduction = self.calculate_survivor_early_retirement_reduction(
				survivor_insurance_benefit_law=benefit_rules.survivor_insurance_benefit_law,
				normal_retirement_age=self.normal_retirement_age,
				retirement_age=self.person.retirement_age)
			self.survivor_insurance_benefit = self.calculate_survivor_insurance_benefit(
				survivor_insurance_benefit_law=benefit_rules.survivor_insurance_benefit_law,
				primary_insurance_amount=self.benefit, 
				deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
				survivor_early_retirement_reduction_factor=self.survivor_early_retirement_reduction, 
				spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
				government_pension_offset=self.government_pension_offset)
			self.save()
		return self