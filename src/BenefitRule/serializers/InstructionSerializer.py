from rest_framework import serializers
from BenefitRule.models import Task, Instruction, Expression

class ExpressionSerializer(serializers.ModelSerializer):
	class Meta:
		model = Expression
		fields = ('order', 'description')

class InstructionSerializer(serializers.ModelSerializer):
	expression_set = ExpressionSerializer(many=True, read_only=True)

	class Meta:
		model = Instruction
		fields = ('expression_set', 'order', 'description')

class TaskSerializer(serializers.ModelSerializer):
	instruction_set = InstructionSerializer(many=True, read_only=True)

	class Meta:
		model = Task
		fields = ('instruction_set',)