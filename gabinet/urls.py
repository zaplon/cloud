"""gabinet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from dashboard.views import *
from visit.rest import IcdViewSet, TemplateViewSet
from result.rest import ResultViewSet
from timetable.rest import TermViewSet
from user_profile.rest import PatientViewSet, DoctorViewSet
from rest_framework import routers
from visit.views import TemplateListView, TabsListView
from utils.views import AjaxFormView


router = routers.DefaultRouter()
router.register(r'icd', IcdViewSet)
router.register(r'results', ResultViewSet)
router.register(r'terms', TermViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'templates', TemplateViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r"^account/", include("account.urls")),
    url(r"^setup/(?P<step>[0-9])", SetupView.as_view(), name='setup'),
    url(r'^$', calendar_view, name='calendar'),
    url(r'^patients/', patients_view, name='patients'),
    url(r'^archive/', archive_view, name='archive'),
    url(r'^profile/', include("user_profile.urls")),
    url(r'^visit/', include("visit.urls"), name='visit'),
    url(r'^icd10/', icd10_view, name='icd10'),
    url(r'^templates/', TemplateListView.as_view(), name='templates'),
    url(r'^tabs/', TabsListView.as_view(), name='tabs'),
    url(r"^rest/", include(router.urls), name='rest'),
    url(r"^timetable/", include("timetable.urls"), name='timetable'),
    url(r"^get-form/", AjaxFormView.as_view(), name='get-form')
]
