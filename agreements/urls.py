from django.conf.urls import url
from views import AgreementView


app_name = 'agreements'
urlpatterns = [
    url(r'^(?P<agreement>[0-9]+)/$', AgreementView.as_view(), name='agreement'),
]