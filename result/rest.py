from django.conf.urls import url, include
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import serializers, viewsets
from .models import Result
from django.conf import settings
from elo.views import getPatientData, getDoc


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ('name', 'description', 'file')


# ViewSets define the view behavior.
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    def retrieve(self, request, *args, **kwargs):
        if settings.USE_ELO:
            return getDoc(request, kwargs['pk'])

    def list(self, request, *args, **kwargs):
        if settings.USE_ELO:
            pesel = False
            if 'search' in request.GET:
                pesel = request.GET['search']
            if 'pesel' in request.GET:
                pesel = request.GET['pesel']
            if not pesel:
                return HttpResponseBadRequest()
            return getPatientData(pesel, request, flat=('is_table' in request.GET))


