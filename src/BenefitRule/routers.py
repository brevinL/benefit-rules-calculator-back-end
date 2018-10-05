from rest_framework.routers import SimpleRouter
from BenefitRule.views import *

BenefitRuleRouter = SimpleRouter()
BenefitRuleRouter.register(f'questions', QuestionList, 'questions')
BenefitRuleRouter.register(r'person', PersonViewSet, 'person')
BenefitRuleRouter.register(r'record', RecordViewSet, 'record')
BenefitRuleRouter.register(r'relationship', RelationshipViewSet, 'relationship')
BenefitRuleRouter.register(r'gpo', GovernmentPensionOffsetViewSet, 'gpo')
