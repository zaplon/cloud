from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^admin/', VisitView.as_view()),
    url(r'template/add/$', TemplateCreate.as_view(), name='template-add'),
    url(r'template/(?P<pk>[0-9]+)/$', TemplateUpdate.as_view(), name='template-update'),
    url(r'template/(?P<pk>[0-9]+)/delete/$', TemplateDelete.as_view(), name='template-delete'),
    url(r'tab/add/$', TabCreate.as_view(), name='tab-add'),
    url(r'tab/(?P<pk>[0-9]+)/$', TabUpdate.as_view(), name='tab-update'),
    url(r'tab/(?P<pk>[0-9]+)/delete/$', TabDelete.as_view(), name='tap-delete')
]
