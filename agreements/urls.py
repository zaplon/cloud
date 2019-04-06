from django.urls import re_path
from agreements.views import AgreementView


app_name = 'agreements'
urlpatterns = [
    re_path(r'^(?P<agreement>[0-9]+)/$', AgreementView.as_view(), name='agreement'),
]
