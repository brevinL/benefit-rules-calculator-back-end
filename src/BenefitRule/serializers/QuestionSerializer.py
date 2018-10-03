from rest_framework import serializers
from BenefitRule.models import Question

class QuestionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Question
		fields = '__all__'