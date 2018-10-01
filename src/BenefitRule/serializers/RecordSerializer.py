from rest_framework import serializers
from BenefitRule.models import Record, Person, Money

from .MoneySerializer import MoneySerializer
from .PersonSerializer import PersonSerializer

class RecordSerializer(serializers.ModelSerializer):
	person = serializers.PrimaryKeyRelatedField(queryset=Person.objects.all())
	average_indexed_monthly_covered_earning = MoneySerializer(required=False, allow_null=True)
	basic_primary_insurance_amount = MoneySerializer(required=False, allow_null=True)
	wep_primary_insurance_amount = MoneySerializer(required=False, allow_null=True)
	average_indexed_monthly_non_covered_earning = MoneySerializer(required=False, allow_null=True)
	monthly_non_covered_pension = MoneySerializer(required=False, allow_null=True)
	wep_reduction = MoneySerializer(required=False, allow_null=True)
	final_primary_insurance_amount = MoneySerializer(required=False, allow_null=True)
	benefit = MoneySerializer(required=False, allow_null=True)
	government_pension_offset = MoneySerializer(required=False, allow_null=True)
	spousal_insurance_benefit = MoneySerializer(required=False, allow_null=True)
	survivor_insurance_benefit = MoneySerializer(required=False, allow_null=True)

	# look into refining redunated code later
	def create(self, validated_data):
		person = validated_data.pop('person')

		data = validated_data.get('average_indexed_monthly_covered_earning')
		if not data is None:
			average_indexed_monthly_covered_earning = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('average_indexed_monthly_covered_earning')
		else:
			average_indexed_monthly_covered_earning = None

		data = validated_data.get('basic_primary_insurance_amount')
		if not data is None:
			basic_primary_insurance_amount = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('basic_primary_insurance_amount')
		else:
			basic_primary_insurance_amount = None

		data = validated_data.get('wep_primary_insurance_amount')
		if not data is None:
			wep_primary_insurance_amount = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('wep_primary_insurance_amount')
		else:
			wep_primary_insurance_amount = None

		data = validated_data.get('average_indexed_monthly_non_covered_earning')
		if not data is None:
			average_indexed_monthly_non_covered_earning = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('average_indexed_monthly_non_covered_earning')
		else:
			average_indexed_monthly_non_covered_earning = None

		data = validated_data.get('monthly_non_covered_pension')
		if not data is None:
			monthly_non_covered_pension = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('monthly_non_covered_pension')
		else:
			monthly_non_covered_pension = None

		data = validated_data.get('wep_reduction')
		if not data is None:
			wep_reduction = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('wep_reduction')
		else:
			wep_reduction = None

		data = validated_data.get('final_primary_insurance_amount')
		if not data is None:
			final_primary_insurance_amount = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('final_primary_insurance_amount')
		else:
			final_primary_insurance_amount = None

		data = validated_data.get('benefit')
		if not data is None:
			benefit = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('benefit')
		else:
			benefit = None

		data = validated_data.get('government_pension_offset')
		if not data is None:
			government_pension_offset = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('government_pension_offset')
		else:
			government_pension_offset = None

		data = validated_data.get('spousal_insurance_benefit')
		if not data is None:
			spousal_insurance_benefit = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('spousal_insurance_benefit')
		else:
			spousal_insurance_benefit = None

		data = validated_data.get('survivor_insurance_benefit')
		if not data is None:
			survivor_insurance_benefit = Money.objects.create(amount=data.get('amount'))
			validated_data.pop('survivor_insurance_benefit')
		else:
			survivor_insurance_benefit = None

		record, created = Record.objects.get_or_create(
			person=person,
			average_indexed_monthly_covered_earning=average_indexed_monthly_covered_earning,
			basic_primary_insurance_amount=basic_primary_insurance_amount,
			wep_primary_insurance_amount=wep_primary_insurance_amount,
			average_indexed_monthly_non_covered_earning=average_indexed_monthly_non_covered_earning,
			monthly_non_covered_pension=monthly_non_covered_pension,
			wep_reduction=wep_reduction,
			final_primary_insurance_amount=final_primary_insurance_amount,
			benefit=benefit,
			government_pension_offset=government_pension_offset,
			spousal_insurance_benefit=spousal_insurance_benefit,
			survivor_insurance_benefit=survivor_insurance_benefit,
			**validated_data
		)

		return record

	class Meta:
		model = Record
		fields = '__all__'

class RecordConfigSerializer(serializers.Serializer):
	partial_update = serializers.BooleanField()
	non_covered_earning_available = serializers.BooleanField()
	covered_earning_available = serializers.BooleanField()