from django.urls import path
from .views import *

urlpatterns = [
    path('cancel/', TermCancelView.as_view(), name='cancel-term'),
    path('move/', TermMoveView.as_view(), name='move-term')
]
