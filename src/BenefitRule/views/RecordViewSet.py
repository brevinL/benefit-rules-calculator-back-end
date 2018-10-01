from rest_framework import viewsets
from BenefitRule.models import Record
from BenefitRule.serializers import RecordSerializer

class RecordViewSet(viewsets.ModelViewSet):
	queryset = Record.objects.all()
	serializer_class = RecordSerializer