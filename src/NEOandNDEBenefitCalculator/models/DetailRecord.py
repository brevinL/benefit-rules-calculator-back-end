from django.db import models
from django.db.models import Max
from BenefitRule.models import Task, DetailRecord, percentage

class DetailRecord(DetailRecord):
	def create_monthly_non_covered_pension_task(self, average_indexed_monthly_non_covered_earning, fraction_of_non_covered_aime_to_non_covered_pension, monthly_non_covered_pension):
		monthly_non_covered_pension_task = Task.objects.create() 
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Get average indexed monthly non covered earning', order=1)
		instruction.expression_set.create(description=f'average indexed monthly non covered earning = {average_indexed_monthly_non_covered_earning}', order=1)
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Get fraction of non covered AIME to non covered pension', order=2)
		instruction.expression_set.create(description=f'fraction of non covered AIME to non covered pension = {fraction_of_non_covered_aime_to_non_covered_pension}', order=1)
		instruction = monthly_non_covered_pension_task.instruction_set.create(description='Multiply average indexed monthly non covered earning with the fraction that was coverted from non covered AIME to non covered pension', order=3)
		instruction.expression_set.create(description='monthly_non_covered_pension = average indexed monthly non covered earning x fraction of non covered AIME to non covered pension', order=1)
		instruction.expression_set.create(description=f'monthly_non_covered_pension = {average_indexed_monthly_non_covered_earning} x {fraction_of_non_covered_aime_to_non_covered_pension}', order=2)
		instruction.expression_set.create(description=f'monthly_non_covered_pension = {monthly_non_covered_pension}', order=3)

		return monthly_non_covered_pension_task

	def create_delay_retirement_credit_task(self, drc_law, year_of_birth, normal_retirement_age, respondent_delay_retirement_credit, max_delay_retirement_credit, delay_retirement_credit):
		delay_retirement_credit_task = drc_law.stepByStep(
			year_of_birth=year_of_birth, 
			normal_retirement_age=normal_retirement_age, 
			delayed_retirement_age=drc_law.age_limit)
		order = delay_retirement_credit_task.instruction_set.aggregate(Max('order')).get('order__max')
		instruction = delay_retirement_credit_task.instruction_set.create(description='Get respondent\'s delay retirement credit', order=order+1)
		instruction.expression_set.create(description=f'respondent\'s delay retirement credit = {percentage(respondent_delay_retirement_credit)}', order=1)
		instruction = delay_retirement_credit_task.instruction_set.create(description='Cap Delay Retirement Credit', order=order+2)
		instruction.expression_set.create(description='delay retirement credit = min(max delay retirement credit, respondent\'s delay retirement credit', order=1)
		instruction.expression_set.create(description=f'delay retirement credit = min({percentage(max_delay_retirement_credit)}, {percentage(respondent_delay_retirement_credit)})', order=2)
		instruction.expression_set.create(description=f'delay retirement credit = {percentage(delay_retirement_credit)}', order=3)

		return delay_retirement_credit_task

	def create_early_retirement_reduction_task(self, primary_err_law, normal_retirement_age, earliest_retirement_age, respondent_early_retirement_reduction, max_early_retirement_reduction, early_retirement_reduction):
		early_retirement_reduction_task = primary_err_law.stepByStep(normal_retirement_age=normal_retirement_age, 
			early_retirement_age=earliest_retirement_age)
		order = early_retirement_reduction_task.instruction_set.aggregate(Max('order')).get('order__max')
		instruction = early_retirement_reduction_task.instruction_set.create(description='Get respondent\'s early retirement reduction', order=order+1)
		instruction.expression_set.create(description=f'respondent\'s early retirement reduction = {percentage(respondent_early_retirement_reduction)}', order=1)
		instruction = early_retirement_reduction_task.instruction_set.create(description='Cap Delay Retirement Credit', order=order+2)
		instruction.expression_set.create(description='early retirement reduction = min(max early retirement reduction, respondent\'s early retirement reduction', order=1)
		instruction.expression_set.create(description=f'early retirement reduction = min({percentage(max_early_retirement_reduction)}, {percentage(respondent_early_retirement_reduction)})', order=2)
		instruction.expression_set.create(description=f'early retirement reduction = {percentage(early_retirement_reduction)}', order=3)

		return early_retirement_reduction_task

	def calculate_retirement_record(self, benefit_rules, beneficiary_record):
		# earliest_retirement_age_task = earliest_retirement_age_law.stepByStep(year_of_birth=self.content_object.year_of_birth)
		# normal_retirement_age_task = normal_retirement_age_law.stepByStep(year_of_birth=self.content_object.year_of_birth)
		average_indexed_monthly_covered_earning_task = self.create_average_indexed_monthly_covered_earning_task(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=self.content_object.annual_covered_earnings)
		basic_primary_insurance_amount_task = self.create_basic_primary_insurance_amount_task(
			pia_law=benefit_rules.pia_law,
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning, 
			year_of_coverage=0)
		wep_primary_insurance_amount_task = self.create_wep_primary_insurance_amount_task(
			wep_pia_law=benefit_rules.wep_pia_law,
			average_indexed_monthly_earning=beneficiary_record.average_indexed_monthly_covered_earning,
			year_of_coverage=self.content_object.years_of_covered_earnings)
		average_indexed_monthly_non_covered_earning_task = self.create_average_indexed_monthly_non_covered_earning_task(
			aime_law=benefit_rules.aime_law,
			taxable_earnings=self.content_object.annual_non_covered_earnings)
		government_pension_offset_task = self.create_government_pension_offset_task(
			gpo_law=benefit_rules.gpo_law, 
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		monthly_non_covered_pension_task = self.create_monthly_non_covered_pension_task(
			average_indexed_monthly_non_covered_earning=beneficiary_record.average_indexed_monthly_non_covered_earning,
			fraction_of_non_covered_aime_to_non_covered_pension=self.content_object.fraction_of_non_covered_aime_to_non_covered_pension,
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		wep_reduction_task = self.create_wep_reduction_task(
			wep_law=benefit_rules.wep_law,
			primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount, 
			wep_primary_insurance_amount=beneficiary_record.wep_primary_insurance_amount,
			monthly_non_covered_pension=beneficiary_record.monthly_non_covered_pension)
		final_primary_insurance_amount_task = self.create_final_primary_insurance_amount_task(
			basic_primary_insurance_amount=beneficiary_record.basic_primary_insurance_amount,
			wep_reduction=beneficiary_record.wep_reduction,
			final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount)
		delay_retirement_credit_task = self.create_delay_retirement_credit_task(
			drc_law=benefit_rules.drc_law,
			year_of_birth=self.content_object.year_of_birth, 
			normal_retirement_age=beneficiary_record.normal_retirement_age, 
			respondent_delay_retirement_credit=self.content_object.delay_retirement_credit,
			delay_retirement_credit=beneficiary_record.delay_retirement_credit, 
			max_delay_retirement_credit=beneficiary_record.max_delay_retirement_credit)
		early_retirement_reduction_task = self.create_early_retirement_reduction_task(
			primary_err_law=benefit_rules.primary_err_law,
			normal_retirement_age=beneficiary_record.normal_retirement_age,
			earliest_retirement_age=beneficiary_record.earliest_retirement_age,
			respondent_early_retirement_reduction=self.content_object.early_retirement_reduction,
			max_early_retirement_reduction=beneficiary_record.max_early_retirement_reduction,
			early_retirement_reduction=beneficiary_record.early_retirement_reduction)
		benefit_task = self.create_benefit_task(
			delay_retirement_credit=beneficiary_record.delay_retirement_credit, 
			early_retirement_reduction=beneficiary_record.early_retirement_reduction, 
			final_primary_insurance_amount=beneficiary_record.final_primary_insurance_amount, 
			benefit=beneficiary_record.benefit)

		return self.update_detail_record(average_indexed_monthly_covered_earning_task=average_indexed_monthly_covered_earning_task,
				basic_primary_insurance_amount_task=basic_primary_insurance_amount_task,
				wep_primary_insurance_amount_task=wep_primary_insurance_amount_task,
				average_indexed_monthly_non_covered_earning_task=average_indexed_monthly_non_covered_earning_task,
				government_pension_offset_task=government_pension_offset_task,
				monthly_non_covered_pension_task=monthly_non_covered_pension_task,
				wep_reduction_task=wep_reduction_task,
				final_primary_insurance_amount_task=final_primary_insurance_amount_task,
				delay_retirement_credit_task=delay_retirement_credit_task,
				early_retirement_reduction_task=early_retirement_reduction_task,
				benefit_task=benefit_task)

	def calculate_survivor_benefits(self, benefit_rules, beneficiary_record, spousal_beneficiary_record, detail_record):
		survivor_early_retirement_reduction = self.content_object.survivor_early_retirement_reduction
		detail_record.survivor_insurance_benefit_task = benefit_rules.survivor_insurance_benefit_law.stepByStep(
			primary_insurance_amount=beneficiary_record.benefit, 
			deceased_spousal_primary_insurance_amount=spousal_beneficiary_record.basic_primary_insurance_amount, 
			survivor_early_retirement_reduction_factor=survivor_early_retirement_reduction, 
			spousal_delay_retirement_factor=spousal_beneficiary_record.delay_retirement_credit,
			government_pension_offset=beneficiary_record.government_pension_offset)
		detail_record.save()
		return detail_record