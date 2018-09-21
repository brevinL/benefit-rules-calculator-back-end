from rest_framework import serializers
from BenefitRule.models import GovernmentPensionOffset

class GovernmentPensionOffsetSerializer(serializers.ModelSerializer):
	class Meta:
		model = GovernmentPensionOffset
		fields = '__all__'