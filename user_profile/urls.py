from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^settings/', SettingsView.as_view(), name='profile-settings')
]