from rest_framework import serializers
from BenefitRule.models import Relationship, Person
from NEOandNDEBenefitCalculator.models import Respondent

from .PersonSerializer import PersonSerializer
from NEOandNDEBenefitCalculator.serializers import RespondentSerializer
from generic_relations.relations import GenericRelatedField

class RelationshipSerializer(serializers.ModelSerializer):
	content_object1 = GenericRelatedField({
		Person: PersonSerializer(),
		Respondent: RespondentSerializer(),
	})

	content_object2 = GenericRelatedField({
		Person: PersonSerializer(),
		Respondent: RespondentSerializer(),
	})

	class Meta:
		model = Relationship
		fields = ('id', 'object_id1', 'object_id2', 'content_object1', 'content_object2', 
			'person1_role', 'person2_role', 'relationship_type', 'start_date', 'end_date')