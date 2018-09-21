from NEOandNDEBenefitCalculator.models import Respondent, Record, DetailRecord
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from BenefitRule.views import PersonViewSet

class RespondentViewSet(PersonViewSet):
	queryset = Respondent.objects.all()
	serializer_class = RespondentSerializer
	
	record_class = Record
	detail_record_class = DetailRecord