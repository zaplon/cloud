from django.conf.urls import url
from medicine.views import *
from dashboard.views import medicines_view

urlpatterns = [
    url(r'^$', medicines_view),
    url(r'(?P<pk>[0-9]+)/', MedicineView.as_view(), name='medicine')
]