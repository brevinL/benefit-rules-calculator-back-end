from rest_framework import serializers
from BenefitRule.models import DetailRecord, Person
from BenefitRule.serializers import TaskSerializer, PersonSerializer

class DetailRecordSerializer(serializers.Serializer):
	person = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
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

	# look into refining redunated code later
	def create(self, validated_data):
		person = validated_data.pop('person')

		data = validated_data.get('average_indexed_monthly_covered_earning_task')
		if not data is None:
			average_indexed_monthly_covered_earning_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('average_indexed_monthly_covered_earning_task')
		else:
			average_indexed_monthly_covered_earning_task = None

		data = validated_data.get('basic_primary_insurance_amount_task')
		if not data is None:
			basic_primary_insurance_amount_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('basic_primary_insurance_amount_task')
		else:
			basic_primary_insurance_amount_task = None

		data = validated_data.get('wep_primary_insurance_amount_task')
		if not data is None:
			wep_primary_insurance_amount_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('wep_primary_insurance_amount_task')
		else:
			wep_primary_insurance_amount_task = None

		data = validated_data.get('average_indexed_monthly_non_covered_earning_task')
		if not data is None:
			average_indexed_monthly_non_covered_earning_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('average_indexed_monthly_non_covered_earning_task')
		else:
			average_indexed_monthly_non_covered_earning_task = None

		data = validated_data.get('monthly_non_covered_pension_task')
		if not data is None:
			monthly_non_covered_pension_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('monthly_non_covered_pension_task')
		else:
			monthly_non_covered_pension_task = None

		data = validated_data.get('wep_reduction_task')
		if not data is None:
			wep_reduction_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('wep_reduction_task')
		else:
			wep_reduction = None

		data = validated_data.get('final_primary_insurance_amount_task')
		if not data is None:
			final_primary_insurance_amount_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('final_primary_insurance_amount_task')
		else:
			final_primary_insurance_amount_task = None

		data = validated_data.get('benefit_task')
		if not data is None:
			benefit_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('benefit_task')
		else:
			benefit_task = None

		data = validated_data.get('government_pension_offset_task')
		if not data is None:
			government_pension_offset_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('government_pension_offset_task')
		else:
			government_pension_offset_task = None

		data = validated_data.get('spousal_insurance_benefit_task')
		if not data is None:
			spousal_insurance_benefit_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('spousal_insurance_benefit_task')
		else:
			spousal_insurance_benefit_task = None

		data = validated_data.get('survivor_insurance_benefit_task')
		if not data is None:
			survivor_insurance_benefit_task = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('survivor_insurance_benefit_task')
		else:
			survivor_insurance_benefit_task = None

		detail_record, created = DetailRecord.objects.get_or_create(
			person=person,
			average_indexed_monthly_covered_earning_task=average_indexed_monthly_covered_earning_task,
			basic_primary_insurance_amount_task=basic_primary_insurance_amount_task,
			wep_primary_insurance_amount_task=wep_primary_insurance_amount_task,
			average_indexed_monthly_non_covered_earning_task=average_indexed_monthly_non_covered_earning_task,
			monthly_non_covered_pension_task=monthly_non_covered_pension_task,
			wep_reduction_task=wep_reduction_task,
			final_primary_insurance_amount_task=final_primary_insurance_amount_task,
			benefit_task=benefit_task,
			government_pension_offset_task=government_pension_offset_task,
			spousal_insurance_benefit_task=spousal_insurance_benefit_task,
			survivor_insurance_benefit_task=survivor_insurance_benefit_task,
			**validated_data
		)

		return detail_record

	class Meta:
		model = DetailRecord
		fields = '__all__'

class DetailRecordConfigSerializer(serializers.Serializer):
	partial_update = serializers.BooleanField()
	non_covered_earning_available = serializers.BooleanField()
	covered_earning_available = serializers.BooleanField()