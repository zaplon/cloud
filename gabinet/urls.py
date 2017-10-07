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
from django.conf.urls.static import static
from django.contrib import admin
from wkhtmltopdf.views import PDFTemplateView

from django.conf import settings
from dashboard.views import *
from visit.rest import IcdViewSet, TemplateViewSet
from result.rest import ResultViewSet
from timetable.rest import TermViewSet
from medicine.rest import *
from user_profile.rest import PatientViewSet, DoctorViewSet, NoteViewSet
from stats.rest import *
from rest_framework import routers
from visit.views import TemplateListView, TabsListView
from g_utils.views import AjaxFormView


router = routers.DefaultRouter()
router.register(r'icd', IcdViewSet)
router.register(r'results', ResultViewSet)
router.register(r'terms', TermViewSet)
router.register(r'patients', PatientViewSet)
router.register(r'doctors', DoctorViewSet)
router.register(r'templates', TemplateViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'medicines', MedicineViewSet)
router.register(r'medicine_parents', MedicineParentViewSet)
router.register(r'refundations', RefundationViewSet)


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^jet/', include('jet.urls', 'jet')),
    url(r"^account/", include("account.urls")),
    url(r"^setup/(?P<step>[0-9])", SetupView.as_view(), name='setup'),
    url(r'^$', index_view, name='index'),
    url(r'^patients/', patients_view, name='patients'),
    url(r'^stats/', stats_view, name='stats'),
    url(r'^calendar/', calendar_view, name='calendar'),
    url(r'^elo/', include("elo.urls"), name='elo'),
    url(r'^archive/$', archive_view, name='archive'),
    url(r'^archive/', include("result.urls"), name='archive'),
    url(r'^profile/', include("user_profile.urls")),
    url(r'^visit/', include("visit.urls"), name='visit'),
    url(r'^icd10/', icd10_view, name='icd10'),
    url(r'^templates/', TemplateListView.as_view(), name='templates'),
    url(r'^medicines/', include("medicine.urls"), name='medicines'),
    url(r'^tabs/', TabsListView.as_view(), name='tabs'),

    url(r'^rest/stats/', Stats.as_view(), name='stats-rest'),
    url(r"^rest/", include(router.urls), name='rest'),

    url(r"^timetable/", include("timetable.urls"), name='timetable'),
    url(r"^get-form/", AjaxFormView.as_view(), name='get-form'),
    url(r"^forms/", include('forms.urls'), name='forms'),
    url(r"^agreements/", include('agreements.urls'), name='agreements'),
    url(r'^pdf/$', PdfView.as_view(template_name='no_pdf.html', filename='result.pdf'), name='pdf'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns