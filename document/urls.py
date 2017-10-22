from django.conf.urls import url
from views import AgreementView


app_name = 'documents'
urlpatterns = [
    url(r'^(?P<document>[0-9]+)/$', DocumentView.as_view(), name='document'),
    url(r'^/print/(?P<document>[0-9]+)/$', PrintDocumentView.as_view(), name='print_document'),
]