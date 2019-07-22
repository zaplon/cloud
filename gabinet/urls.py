"""gabinet URL Configuration

The `re_pathpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/re_paths/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to re_pathpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to re_pathpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.re_paths import re_path, include
    2. Add a URL to re_pathpatterns:  re_path(r'^blog/', include('blog.re_paths'))
"""
from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.static import static
from django.contrib import admin

from agreements.api.agreements import AgreementApiView, AgreementToUserApiView
from examination.rest import ExaminationViewSet, ExaminationCategoryViewSet
from user_profile.sms_verification import GabinetLoginView, SMSCodeViewSet, SMSValidationView
from visit.rest import IcdViewSet, TemplateViewSet, VisitViewSet, TabViewSet, PopularIcdViewSet
from result.rest import ResultViewSet
from timetable.rest import TermViewSet, ServiceViewSet, LocalizationViewSet, BookingViewSet, TermlistView
from medicine.rest import *
from user_profile.rest import PatientViewSet, DoctorViewSet, NoteViewSet, UserDetailsView, SpecializationViewSet, \
    UserViewSet, PermissionViewSet, GroupViewSet, SystemSettingsViewSet, InfoViewSet
from stats.rest import *
from rest_framework import routers
from visit.views import TemplateListView, TabsListView
from g_utils.views import AjaxFormView, PDFView

router = routers.DefaultRouter()
router.register(r'icd/popular', PopularIcdViewSet)
router.register(r'icd', IcdViewSet)
router.register(r'results', ResultViewSet)
router.register(r'terms', TermViewSet)
router.register(r'terms_list', TermlistView)
router.register(r'info', InfoViewSet)
router.register(r'booking', BookingViewSet)
router.register(r'localizations', LocalizationViewSet)
router.register(r'services', ServiceViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'users', UserViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'groups', GroupViewSet)
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
router.register(r'examinations', ExaminationViewSet, base_name='examinations')
router.register(r'examinations_categories', ExaminationCategoryViewSet, base_name='examinations_categories')
router.register(r'settings', SystemSettingsViewSet, base_name='settings')
router.register(r'agreements', AgreementApiView, base_name='agreements')
router.register(r'agreements_to_users', AgreementToUserApiView, base_name='agreements_to_users')
router.register(r'sms', SMSCodeViewSet, base_name='sms')


urlpatterns = [
    re_path(r'^admin/', admin.site.urls),
    # re_path(r'^jet_api/', include(jet_re_paths)),
    re_path(r"^account/", include("account.urls")),
    re_path(r'^archive/', include("result.urls"), name='archive'),
    re_path(r'^profile/', include("user_profile.urls")),
    re_path(r'^visit/', include("visit.urls"), name='visit'),
    re_path(r'^templates/', TemplateListView.as_view(), name='templates'),
    re_path(r'^tabs/', TabsListView.as_view(), name='tabs'),

    re_path(r'^rest/stats/', Stats.as_view(), name='stats-rest'),
    re_path(r'^rest/user/', UserDetailsView.as_view(), name='user-details'),
    re_path(r'^rest/sms/validate_code', SMSValidationView.as_view(), name='sms-validate'),

    re_path(r"^rest/", include((router.urls, 'rest'), namespace='rest')),

    re_path(r'^pdf/', PDFView.as_view(), name='generate-pdf'),

    re_path(r"^timetable/", include(("timetable.urls", 'timetable'), namespace='timetable')),
    re_path(r"^get-form/", AjaxFormView.as_view(), name='get-form'),
    re_path(r"^forms/", include('forms.urls'), name='forms'),
    re_path(r"^backend/forms/", include('forms.urls'), name='forms'),
    re_path(r"^agreements/", include('agreements.urls'), name='agreements'),
    re_path(r"^rest-auth/login/$", GabinetLoginView.as_view(), name="login"),
    re_path(r'^rest-auth/', include('rest_auth.urls'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
