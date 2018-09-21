from rest_framework import viewsets
from rest_framework.decorators import action
from BenefitRule.models import GovernmentPensionOffset, Money
from BenefitRule.serializers import TaskSerializer, MoneySerializer, GovernmentPensionOffsetSerializer
from rest_framework.response import Response

class GovernmentPensionOffsetViewSet(viewsets.ReadOnlyModelViewSet):
	queryset = GovernmentPensionOffset.objects.all()
	serializer_class = GovernmentPensionOffsetSerializer

	# need to be able to handle record id or request record
	@action(methods=['post'], detail=True)
	def calculate(self, request, pk=None):
		serializer = MoneySerializer(data=request.data)
		if serializer.is_valid():
			monthly_non_covered_pension = Money(**serializer.validated_data)

			gpo_rule = self.get_object()
			gpo = gpo_rule.calculate(monthly_non_covered_pension=monthly_non_covered_pension)

			gpo_serializer = MoneySerializer(gpo)
			return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	@action(methods=['post'], detail=True)
	def stepByStep(self, request, pk=None):
		serializer = MoneySerializer(data=request.data)
		if serializer.is_valid():
			monthly_non_covered_pension = Money(**serializer.validated_data)
			
			gpo_rule = self.get_object()
			gpo_task = gpo_rule.stepByStep(monthly_non_covered_pension=monthly_non_covered_pension)

			gpo_serializer = TaskSerializer(gpo_task)
			return Response(gpo_serializer.data, content_type='application/json;charset=utf-8')