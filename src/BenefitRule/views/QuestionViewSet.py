from rest_framework import viewsets
from BenefitRule.models import Question
from BenefitRule.serializers import QuestionSerializer
from rest_framework import generics

class QuestionList(viewsets.ViewSetMixin, generics.ListAPIView):
	serializer_class = QuestionSerializer

	def get_queryset(self):
		queryset = []
		benefit_rule = self.request.query_params.get('benefit-rule', None)
		if benefit_rule is not None:
			for choice in Question.BENEFIT_RULE_CHOICES:
				if choice[0] == benefit_rule:
					queryset = Question.objects.filter(benefit_rule=choice[0])
		return queryset