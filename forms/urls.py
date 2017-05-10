from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'show_form/', FormView.as_view(), name='show_form'),
    url(r'edit_form/', EditFormView.as_view(), name='edit_form'),
    url(r'get_form/', get_form, name='get_form')
]
