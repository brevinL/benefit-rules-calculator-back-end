from django.db import models

class Question(models.Model):
	# find a way to api the choices
	WEP = 'windfall-elimination-provision'
	GPO = 'government-pension-offset'
	BENEFIT_RULE_CHOICES = (
		(WEP, 'Windfall Elimination Pension'),
		(GPO, 'Government Pension Offset'),
	)
	benefit_rule = models.CharField(
		max_length=120,
		choices=BENEFIT_RULE_CHOICES,
	)

	number = 'number',
	currency = 'currency'
	default = 'default'
	CONTROL_TYPE_CHOICES = (
		(number, 'number'),
		(currency, 'currency'),
	)
	controlType = models.CharField(
		max_length=10,
		choices=CONTROL_TYPE_CHOICES,
	)
	key = models.TextField()
	value = models.TextField(blank=True)
	label = models.TextField()
	required = models.BooleanField(default=True)
	order = models.PositiveIntegerField()

	min = models.IntegerField(blank=True, null=True)
	max = models.IntegerField(blank=True, null=True)