from rest_framework import viewsets
from BenefitRule.models import Question
from BenefitRule.serializers import QuestionSerializer

class QuestionViewSet(viewsets.ModelViewSet):
	queryset = Question.objects.all()
	serializer_class = QuestionSerializer