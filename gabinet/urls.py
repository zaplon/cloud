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
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin

from dashboard.views import *
from visit.rest import IcdViewSet, TemplateViewSet, VisitViewSet, TabViewSet
from result.rest import ResultViewSet
from timetable.rest import TermViewSet, ServiceViewSet, LocalizationViewSet, BookingViewSet
from medicine.rest import *
from user_profile.rest import PatientViewSet, DoctorViewSet, NoteViewSet, UserDetailsView, SpecializationViewSet
from stats.rest import *
from rest_framework import routers
from visit.views import TemplateListView, TabsListView
from g_utils.views import AjaxFormView


router = routers.DefaultRouter()
router.register(r'icd', IcdViewSet)
router.register(r'results', ResultViewSet)
router.register(r'terms', TermViewSet)
router.register(r'booking', BookingViewSet)
router.register(r'localizations', LocalizationViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'specializations', SpecializationViewSet)
router.register(r'templates', TemplateViewSet)
router.register(r'tabs', TabViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'medicines', MedicineViewSet, base_name='medicines')
router.register(r'medicine_parents', MedicineParentViewSet, base_name='medicine_parents')
router.register(r'refundations', RefundationViewSet)
router.register(r'prescriptions', PrescriptionViewSet)
router.register(r'visits', VisitViewSet, base_name='visits')


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    # url(r'^jet_api/', include(jet_urls)),
    url(r"^account/", include("account.urls")),
    url(r"^setup/(?P<step>[0-9])", SetupView.as_view(), name='setup'),
    url(r'^patients/', patients_view, name='patients'),
    url(r'^stats/', stats_view, name='stats'),
    url(r'^prescriptions/', prescriptions_view, name='prescriptions'),
    url(r'^calendar/', calendar_view, name='calendar'),
    url(r'^archive/$', archive_view, name='archive'),
    url(r'^archive/', include("result.urls"), name='archive'),
    url(r'^profile/', include("user_profile.urls")),
    url(r'^visit/', include("visit.urls"), name='visit'),
    url(r'^icd10/', icd10_view, name='icd10'),
    url(r'^templates/', TemplateListView.as_view(), name='templates'),
    url(r'^medicines/', include("medicine.urls"), name='medicines'),
    url(r'^tabs/', TabsListView.as_view(), name='tabs'),

    url(r'^rest/stats/', Stats.as_view(), name='stats-rest'),
    url(r'^rest/user/', UserDetailsView.as_view(), name='user-details'),
    url(r"^rest/", include(router.urls, namespace='rest')),

    url(r"^timetable/", include("timetable.urls"), name='timetable'),
    url(r"^get-form/", AjaxFormView.as_view(), name='get-form'),
    url(r"^forms/", include('forms.urls'), name='forms'),
    url(r"^agreements/", include('agreements.urls'), name='agreements'),
    url(r'^pdf/$', PdfView.as_view(template_name='no_pdf.html', filename='result.pdf'), name='pdf'),
    url(r'^rest-auth/', include('rest_auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
