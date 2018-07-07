from django.conf.urls import url
from medicine.views import *

urlpatterns = [
    url(r'^prescription-numbers/', AddPrescriptionNumbersView.as_view()),
]