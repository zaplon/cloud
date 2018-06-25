from django.conf.urls import url
from medicine.views import *
from dashboard.views import medicines_view

urlpatterns = [
    url(r'^$', medicines_view),
]