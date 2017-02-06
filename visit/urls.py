from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from .views import *

urlpatterns = [
    url(r'template/add/$', TemplateCreate.as_view(), name='template-add'),
    url(r'template/(?P<pk>[0-9]+)/$', TemplateUpdate.as_view(), name='template-update'),
    url(r'template/(?P<pk>[0-9]+)/delete/$', TemplateDelete.as_view(), name='template-delete'),
    url(r'tab/add/$', TabCreate.as_view(), name='tab-add'),
    url(r'tab/enable/$', enable_tab, name='tab-enable'),
    url(r'tab/(?P<pk>[0-9]+)/$', TabUpdate.as_view(), name='tab-update'),
    url(r'tab/(?P<pk>[0-9]+)/delete/$', TabDelete.as_view(), name='tab-delete'),
    url(r'pdf/(?P<pk>[0-9]+)/', PdfView.as_view(), name='visit-pdf'),
    url(r'(?P<pk>[0-9]+)/', login_required(VisitView.as_view()), name='visit')
]
