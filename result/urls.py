from django.urls import re_path
from .views import *


urlpatterns = [
    re_path(r'^new', ResultCreateView.as_view(), name='new-document'),
    re_path(r'edit/(?P<pk>[0-9]+)/$', ResultUpdateView.as_view(), name='edit-document'),
    re_path(r'delete/(?P<pk>[0-9]+)/$', ResultDeleteView.as_view(), name='delete-document'),
    re_path(r'(?P<pk>[0-9]+)/$', ResultDetailView.as_view(), name='view-document'),
    re_path(r'^search', search_view, name='search-document')
]
