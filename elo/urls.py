from django.conf.urls import url
from views import getDoc, getPatientData

urlpatterns = [
    url(r'getDoc/(?P<id>\d+)', getDoc, name='get_doc'),
    url(r'get_archive', getPatientData, name='get_archive')
]
