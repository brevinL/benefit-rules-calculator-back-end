from datetime import date
from django.db.models import Q, Max
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action 
from rest_framework.response import Response
from BenefitRule.models import BenefitRule, Relationship, Record, DetailRecord, Person, RecordConfig
from BenefitRule.serializers import RecordSerializer, DetailRecordSerializer, PersonSerializer, RecordConfigSerializer
from NEOandNDEBenefitCalculator.models import Respondent
from django.contrib.contenttypes.models import ContentType

# fix to able to post only
# redudant code just to reference a overrided record and detail record managers
class PersonViewSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer

	record_class = Record
	detail_record_class = DetailRecord

	@action(methods=['post'], detail=True)
	def get_updated_record(self, request, pk=None): # given an inital record -> applied benefit rules to record -> update record
		start_date = BenefitRule.objects.aggregate(Max('start_date')).get('start_date__max') 
		end_date = BenefitRule.objects.aggregate(Max('end_date')).get('end_date__max')
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=start_date, end_date__gte=end_date)
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()
		person_type = ContentType.objects.get_for_model(person)
		try:
			record = self.record_class.objects.get(content_type__pk=person_type.id, object_id=person.id)
		except self.record_class.DoesNotExist:
			record = self.record_class(content_object=person)
			record.save()

		config_serializer = RecordConfigSerializer(data=request.data.get('config', None))
		if not config_serializer.is_valid():
			return Response({'detail': config_serializer.errors}, content_type='application/json;charset=utf-8', status=status.HTTP_400_BAD_REQUEST)
		config = RecordConfig(config_serializer.data)

		record = record.calculate_retirement_record(benefit_rules=benefit_rules, config=config)

		respondent_married_relationships = Relationship.objects.filter(
			(Q(content_type1__pk=person_type.id) & Q(object_id1=person.id)) | 
			(Q(content_type2__pk=person_type.id) & Q(object_id2=person.id)), 
			relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			try:
				person_type = ContentType.objects.get_for_model(spouse)
				spouse_record = self.record_class.objects.get(content_type__pk=person_type.id, object_id=spouse.id)
			except self.record_class.DoesNotExist:
				spouse_record = self.record_class(content_object=spouse)
				spouse_record.save()
			spouse_record = spouse_record.calculate_retirement_record(benefit_rules=benefit_rules, config=config)

			record = record.calculate_dependent_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=spouse_record, config=config)
			record = record.calculate_survivor_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=spouse_record, config=config)
			
			spouse_record = spouse_record.calculate_dependent_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=record, config=config) 
			spouse_record = spouse_record.calculate_survivor_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=record, config=config)

		record_serializer = RecordSerializer(record, context={'request': request})
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)

	@action(methods=['post'], detail=True)
	def get_updated_detail_record(self, request, pk=None):
		start_date = BenefitRule.objects.aggregate(Max('start_date')).get('start_date__max') 
		end_date = BenefitRule.objects.aggregate(Max('end_date')).get('end_date__max')
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=start_date, end_date__gte=end_date)
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()

		try:
			person_type = ContentType.objects.get_for_model(person)
			record = self.record_class.objects.get(content_type__pk=person_type.id, object_id=person.id)
		except self.record_class.DoesNotExist:
			return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)
		
		try:
			person_type = ContentType.objects.get_for_model(person)
			detail_record = self.detail_record_class.objects.get(content_type__pk=person_type.id, object_id=person.id)
		except self.detail_record_class.DoesNotExist:
			detail_record = self.detail_record_class(content_object=person)
			detail_record.save()

		detail_record = detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record)

		respondent_married_relationships = Relationship.objects.filter(
			(Q(content_type1__pk=person_type.id) & Q(object_id1=person.id)) | 
			(Q(content_type2__pk=person_type.id) & Q(object_id2=person.id)), 
			relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(content_object=person)
			try:
				person_type = ContentType.objects.get_for_model(spouse)
				spouse_record = self.record_class.objects.get(content_type__pk=person_type.id, object_id=spouse.id)
			except self.record_class.DoesNotExist:
				return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

			try:
				person_type = ContentType.objects.get_for_model(person)
				spouse_detail_record = self.detail_record_class.objects.get(content_type__pk=person_type.id, object_id=spouse.id)
			except self.detail_record_class.DoesNotExist:
				spouse_detail_record = self.detail_record_class(content_object=spouse)
				spouse_detail_record.save()

			spouse_detail_record = spouse_detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record)

			detail_record = detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)
			detail_record = detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, detail_record=detail_record)

			spouse_detail_record = spouse_detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)
			spouse_detail_record = spouse_detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, detail_record=spouse_detail_record)

		detail_record_serializer = DetailRecordSerializer(instance=detail_record, context={'request': request})
		return Response(detail_record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)