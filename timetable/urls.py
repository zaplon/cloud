from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^calendar/', CalendarView.as_view(), name='profile-settings')
]