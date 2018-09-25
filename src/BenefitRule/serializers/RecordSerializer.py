from rest_framework import serializers
from BenefitRule.models import Record, Person
from NEOandNDEBenefitCalculator.models import Respondent
from .MoneySerializer import MoneySerializer

from .PersonSerializer import PersonSerializer
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from generic_relations.relations import GenericRelatedField

class RecordSerializer(serializers.ModelSerializer):
	content_object = GenericRelatedField({
		Person: PersonSerializer(),
		Respondent: RespondentSerializer(),
	})

	average_indexed_monthly_covered_earning = MoneySerializer()
	basic_primary_insurance_amount = MoneySerializer()
	wep_primary_insurance_amount = MoneySerializer()
	average_indexed_monthly_non_covered_earning = MoneySerializer()
	monthly_non_covered_pension = MoneySerializer()
	wep_reduction = MoneySerializer()
	final_primary_insurance_amount = MoneySerializer()
	benefit = MoneySerializer()
	government_pension_offset = MoneySerializer()
	spousal_insurance_benefit = MoneySerializer()
	survivor_insurance_benefit = MoneySerializer()

	class Meta:
		model = Record
		fields = ('id', 'object_id', 'content_object', 
			'average_indexed_monthly_covered_earning', 'basic_primary_insurance_amount', 
			'wep_primary_insurance_amount', 'average_indexed_monthly_non_covered_earning', 
			'monthly_non_covered_pension', 'wep_reduction', 'final_primary_insurance_amount',
			'benefit', 'government_pension_offset', 'spousal_insurance_benefit', 'survivor_insurance_benefit')

class RecordConfigSerializer(serializers.Serializer):
	partial_update = serializers.BooleanField()
	non_covered_earning_available = serializers.BooleanField()
	covered_earning_available = serializers.BooleanField()