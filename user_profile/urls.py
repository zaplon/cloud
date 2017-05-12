from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^settings/', SettingsView.as_view(), name='profile-settings'),
    url(r'^patients/new', PatientCreateView.as_view(), name='new-patient'),
    url(r'^add_recipes/', add_recipes, name='add-recipes'),
    url(r'^patients/(?P<pk>[0-9]+)/delete/$', PatientDeleteView.as_view(), name='patient-delete'),
    url(r'patients/(?P<pk>[0-9]+)/$', PatientUpdateView.as_view(), name='patient-update'),
]