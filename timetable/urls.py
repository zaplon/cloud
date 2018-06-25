from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from .views import *

urlpatterns = [
    url(r'^cancel/', TermCancelView.as_view(), name='cancel-term'),
    url(r'^move/', TermMoveView.as_view(), name='move-term')
]