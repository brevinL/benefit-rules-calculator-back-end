from django.contrib import admin
from .models import *

admin.site.register(RetirementAge)
admin.site.register(SurvivorInsuranceBenefit)
admin.site.register(EarlyRetirementBenefitReduction)
admin.site.register(GovernmentPensionOffset)
admin.site.register(DelayRetirementCredit)
admin.site.register(WindfallEliminationProvision)
admin.site.register(AverageIndexedMonthlyEarning)
admin.site.register(PrimaryInsuranceAmount)
admin.site.register(SpousalInsuranceBenefit)

admin.site.register(Record)
admin.site.register(Money)
admin.site.register(Person)
admin.site.register(Relationship)

admin.site.register(BenefitRule)

admin.site.register(Task)
admin.site.register(Instruction)
admin.site.register(Expression)