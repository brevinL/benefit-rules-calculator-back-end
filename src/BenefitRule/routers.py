from rest_framework.routers import SimpleRouter
from BenefitRule.views import *

BenefitRuleRouter = SimpleRouter()
BenefitRuleRouter.register(r'person', PersonViewSet, 'person')
BenefitRuleRouter.register(r'relationship', RelationshipViewSet, 'relationship')
BenefitRuleRouter.register(r'gpo', GovernmentPensionOffsetViewSet, 'gpo')
