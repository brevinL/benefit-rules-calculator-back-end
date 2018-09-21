from rest_framework import status, viewsets, serializers
from BenefitRule.models import Relationship
from BenefitRule.serializers import RelationshipSerializer
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from NEOandNDEBenefitCalculator.models import Respondent
from django.db.models import Q

# fix to able to post only
class RelationshipViewSet(viewsets.ViewSetMixin, generics.ListCreateAPIView, generics.RetrieveAPIView):
	serializer_class = RelationshipSerializer

	def get_queryset(self):
		queryset = Relationship.objects.all()
		if self.request.method == 'GET':
			respondent_id = self.request.query_params.get('respondent', None)
			if respondent_id:
				respondent = Respondent.objects.get(id=respondent_id)
				queryset = Relationship.objects.filter(Q(person1=respondent) | Q(person2=respondent), relationship_type=Relationship.MARRIED)
		return queryset