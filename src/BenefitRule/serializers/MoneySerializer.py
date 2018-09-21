from rest_framework import serializers
from BenefitRule.models import Money

class MoneySerializer(serializers.ModelSerializer):
	class Meta:
		model = Money
		fields = ('amount', )