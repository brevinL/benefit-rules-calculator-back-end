from datetime import date
from django.db.models import Q, Max
from rest_framework import status, viewsets, serializers
from rest_framework.decorators import action 
from rest_framework.response import Response
from BenefitRule.models import BenefitRule, Relationship, Record, DetailRecord, Person, RecordConfig, DetailRecordConfig
from BenefitRule.serializers import RecordSerializer, DetailRecordSerializer, PersonSerializer, RecordConfigSerializer, DetailRecordConfigSerializer

# redudant code just to reference a overrided record and detail record managers
class PersonViewSet(viewsets.ModelViewSet):
	queryset = Person.objects.all()
	serializer_class = PersonSerializer

	record_class = Record
	detail_record_class = DetailRecord

	@action(methods=['get', 'post'], detail=True)
	def get_updated_record(self, request, pk=None): # given an inital record -> applied benefit rules to record -> update record
		start_date = BenefitRule.objects.aggregate(Max('start_date')).get('start_date__max') 
		end_date = BenefitRule.objects.aggregate(Max('end_date')).get('end_date__max')
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=start_date, end_date__gte=end_date)
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()
		try:
			record = self.record_class.objects.get(person=person)
		except self.record_class.DoesNotExist:
			record = self.record_class.objects.create(person=person)

		request_config = request.data.get('config', None)
		if not request_config is None:
			config_serializer = RecordConfigSerializer(data=request_config)
			if not config_serializer.is_valid():
				return Response({'detail': config_serializer.errors}, content_type='application/json;charset=utf-8', status=status.HTTP_400_BAD_REQUEST)
			config = RecordConfig(config_serializer.data)
		else:
			config = None

		record = record.calculate_retirement_record(benefit_rules=benefit_rules, config=config)

		respondent_married_relationships = Relationship.objects.filter(
			Q(person1=person) | Q(person2=person),
			relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(person=person)
			try:
				spouse_record = self.record_class.objects.get(person=spouse)
			except self.record_class.DoesNotExist:
				spouse_record = self.record_class.objects.create(person=spouse)
			spouse_record = spouse_record.calculate_retirement_record(benefit_rules=benefit_rules, config=config)

			record = record.calculate_dependent_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=spouse_record, config=config)
			record = record.calculate_survivor_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=spouse_record, config=config)
			
			spouse_record = spouse_record.calculate_dependent_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=record, config=config) 
			spouse_record = spouse_record.calculate_survivor_benefits(benefit_rules=benefit_rules, spousal_beneficiary_record=record, config=config)

		record_serializer = RecordSerializer(record, context={'request': request})
		return Response(record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)

	@action(methods=['get', 'post'], detail=True)
	def get_updated_detail_record(self, request, pk=None):
		start_date = BenefitRule.objects.aggregate(Max('start_date')).get('start_date__max') 
		end_date = BenefitRule.objects.aggregate(Max('end_date')).get('end_date__max')
		try:
			benefit_rules = BenefitRule.objects.get(start_date__lte=start_date, end_date__gte=end_date)
		except BenefitRule.DoesNotExist:
			return Response({'detail': 'No Benefit Rules match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

		person = self.get_object()

		try:
			record = self.record_class.objects.get(person=person)
		except self.record_class.DoesNotExist:
			return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)
		
		try:
			detail_record = self.detail_record_class.objects.get(person=person)
		except self.detail_record_class.DoesNotExist:
			detail_record = self.detail_record_class.objects.create(person=person)

		request_config = request.data.get('config', None)
		if not request_config is None:
			config_serializer = DetailRecordConfigSerializer(data=request_config)
			if not config_serializer.is_valid():
				return Response({'detail': config_serializer.errors}, content_type='application/json;charset=utf-8', status=status.HTTP_400_BAD_REQUEST)
			config = DetailRecordConfig(config_serializer.data)
		else:
			config = None

		detail_record = detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record, config=config)

		respondent_married_relationships = Relationship.objects.filter(
			Q(person1=person) | Q(person2=person), 
			relationship_type=Relationship.MARRIED)
		for relationship in respondent_married_relationships:
			spouse = relationship.get_other(person=person)
			try:
				spouse_record = self.record_class.objects.get(person=spouse)
			except self.record_class.DoesNotExist:
				return Response({'detail': 'No Record match the given query'}, content_type='application/json;charset=utf-8', status=status.HTTP_404_NOT_FOUND)

			try:
				spouse_detail_record = self.detail_record_class.objects.get(person=spouse)
			except self.detail_record_class.DoesNotExist:
				spouse_detail_record = self.detail_record_class.objects.create(person=spouse)

			spouse_detail_record = spouse_detail_record.calculate_retirement_record(benefit_rules=benefit_rules, beneficiary_record=record, config=config)

			detail_record = detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, config=config)
			detail_record = detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=record, spousal_beneficiary_record=spouse_record, config=config)

			spouse_detail_record = spouse_detail_record.calculate_dependent_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, config=config)
			spouse_detail_record = spouse_detail_record.calculate_survivor_benefits(benefit_rules=benefit_rules, beneficiary_record=spouse_record, spousal_beneficiary_record=record, config=config)

		detail_record_serializer = DetailRecordSerializer(instance=detail_record, context={'request': request})
		return Response(detail_record_serializer.data, content_type='application/json;charset=utf-8', status=status.HTTP_200_OK)