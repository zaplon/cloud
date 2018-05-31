from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from .views import *

urlpatterns = [
    url(r'show_form/', FormView.as_view(), name='show_form'),
    url(r'edit_form/', csrf_exempt(EditFormView.as_view()), name='edit_form'),
    url(r'get_form/', get_form, name='get_form')
]
