from rest_framework import serializers
from BenefitRule.models import Relationship, Person
from .PersonSerializer import PersonSerializer

class RelationshipSerializer(serializers.ModelSerializer):
	person1 = PersonSerializer()
	person2 = PersonSerializer()

	def create(self, validated_data):
		person1_data = validated_data.pop('person1')
		person2_data = validated_data.pop('person2')

		person1 = Person.objects.create(**person1_data)
		person2 = Person.objects.create(**person2_data)
		return Relationship.objects.create(
			person1=person1, person2=person2, **validated_data)

	class Meta:
		model = Relationship
		fields = '__all__'