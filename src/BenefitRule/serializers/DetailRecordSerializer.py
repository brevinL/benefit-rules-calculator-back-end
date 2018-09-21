from rest_framework import serializers
from BenefitRule.models import Person
from NEOandNDEBenefitCalculator.models import Respondent, DetailRecord
from BenefitRule.serializers import TaskSerializer, InstructionSerializer, ExpressionSerializer, PersonSerializer, RespondentSerializer
from generic_relations.relations import GenericRelatedField

class DetailRecordSerializer(serializers.Serializer):
	content_object = GenericRelatedField({
		Person: PersonSerializer(),
		Respondent: RespondentSerializer()
	})
	# earliest_retirement_age_task = InstructionSerializer()
	# normal_retirement_age_task = InstructionSerializer()
	average_indexed_monthly_covered_earning_task = TaskSerializer()
	basic_primary_insurance_amount_task = TaskSerializer()
	wep_primary_insurance_amount_task = TaskSerializer()
	average_indexed_monthly_non_covered_earning_task = TaskSerializer()
	monthly_non_covered_pension_task = TaskSerializer()
	wep_reduction_task = TaskSerializer()
	final_primary_insurance_amount_task = TaskSerializer()
	delay_retirement_credit_task = TaskSerializer()
	early_retirement_reduction_task = TaskSerializer()
	benefit_task = TaskSerializer()
	government_pension_offset_task = TaskSerializer()
	spousal_insurance_benefit_task = TaskSerializer()
	survivor_insurance_benefit_task = TaskSerializer()

	class Meta:
		model = DetailRecord
		fields = ('id', 'object_id', 'content_object',
			# 'earliest_retirement_age_task', 'normal_retirement_age_task', 
			'average_indexed_monthly_covered_earning_task_task', 'basic_primary_insurance_amount_task', 
			'wep_primary_insurance_amount_task', 'average_indexed_monthly_non_covered_earning_task', 
			'monthly_non_covered_pension_task', 'wep_reduction_task', 'final_primary_insurance_amount_task',
			'max_delay_retirement_credit_task', 'delay_retirement_credit_task', 
			'max_early_retirement_reduction_task', 'early_retirement_reduction_task',
			'benefit_task', 'government_pension_offset_task', 'spousal_insurance_benefit_task', 
			'survivor_insurance_benefit_task')