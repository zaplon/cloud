from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^new', ResultCreateView.as_view(), name='new-document')
]
