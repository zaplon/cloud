from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^new', ResultCreateView.as_view(), name='new-document'),
    url(r'edit/(?P<pk>[0-9]+)/$', ResultUpdateView.as_view(), name='edit-document'),
    url(r'delete/(?P<pk>[0-9]+)/$', ResultDeleteView.as_view(), name='delete-document'),
    url(r'(?P<pk>[0-9]+)/$', ResultDetailView.as_view(), name='view-document'),
    url(r'^search', search_view, name='search-document')
]
