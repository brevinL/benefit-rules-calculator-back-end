from rest_framework import serializers
from BenefitRule.models import BenefitRule

class BenefitRuleSerializer(serializers.ModelSerializer):
	class Meta:
		model = BenefitRule
		fields = ('start_date', 'end_date')