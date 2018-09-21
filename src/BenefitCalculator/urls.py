"""BenefitCalculator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from BenefitRule.routers import BenefitRuleRouter
from NEOandNDEBenefitCalculator.routers import NEONDERouter

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/benefit-rule/', include((BenefitRuleRouter.urls, 'BenefitRule'), namespace='benefit-rule')), 
    url(r'^api/neo-and-nde-benefit-calculator/', include((NEONDERouter.urls, 'NEOandNDEBenefitCalculator'), namespace='neo-and-nde-benefit-calculator')), 
]

urlpatterns = format_suffix_patterns(urlpatterns) 