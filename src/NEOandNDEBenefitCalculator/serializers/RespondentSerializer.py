from rest_framework import serializers
from BenefitRule.models import Money
from NEOandNDEBenefitCalculator.models import Respondent
from BenefitRule.serializers import MoneySerializer

# class RespondentListSerializer(serializers.ListSerializer):
# 	def create(self, validated_data):
# 		respondents = []
# 		for item in validated_data:
# 			annual_covered_earning = item.get('annual_covered_earning')
# 			item['annual_covered_earning'] = Money.objects.create(amount=annual_covered_earning.get('amount', 0))
# 			annual_non_covered_earning = item.get('annual_non_covered_earning')
# 			item['annual_non_covered_earning'] = Money.objects.create(amount=annual_non_covered_earning.get('amount', 0))
# 			respondents.append(Respondent.objects.create(**item))
# 		return respondents
		
class RespondentSerializer(serializers.ModelSerializer):
	# id = serializers.IntegerField() 
	# alias = serializers.CharField(allow_null=True)
	annual_covered_earning = MoneySerializer()
	annual_non_covered_earning = MoneySerializer()
	# spousal_early_retirement_reduction = MoneySerializer()
	# survivor_early_retirement_reduction = MoneySerializer()

	class Meta:
		model = Respondent
		fields = '__all__'
		# list_serializer_class = RespondentListSerializer

	def create(self, validated_data):
		annual_covered_earning_data = validated_data.pop('annual_covered_earning')
		annual_non_covered_earning_data = validated_data.pop('annual_non_covered_earning')
		annual_covered_earning = Money.objects.create(amount=annual_covered_earning_data.get('amount', 0))
		annual_non_covered_earning = Money.objects.create(amount=annual_non_covered_earning_data.get('amount', 0))
		respondent = Respondent.objects.create(
			annual_covered_earning=annual_covered_earning, 
			annual_non_covered_earning=annual_non_covered_earning, 
			**validated_data)

		return respondent