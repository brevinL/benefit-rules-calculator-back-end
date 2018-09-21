from rest_framework import serializers
from NEOandNDEBenefitCalculator.models import DetailRecord
from BenefitRule.serializers import TaskSerializer, InstructionSerializer, ExpressionSerializer

class DetailRecordSerializer(serializers.Serializer):
	person_id = serializers.IntegerField()
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
		fields = '__all__'