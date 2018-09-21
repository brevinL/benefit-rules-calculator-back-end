from rest_framework.routers import SimpleRouter
from NEOandNDEBenefitCalculator.views import *

NEONDERouter = SimpleRouter()
NEONDERouter.register(r'respondents', RespondentViewSet)