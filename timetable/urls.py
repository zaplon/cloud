from django.conf.urls import url

from .views import *

urlpatterns = [
    url(r'^calendar/', CalendarView.as_view(), name='profile-settings'),
    url(r'^cancel/', term_cancel_view, name='cancel-term'),
    url(r'^move/', term_move_view, name='move-term')
]