from django.conf.urls import url, include
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import serializers, viewsets
from .models import Result
from django.conf import settings
from elo.views import getPatientData, getDoc
from django_filters.rest_framework import DjangoFilterBackend


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ('name', 'description', 'file')


# ViewSets define the view behavior.
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_fields = ('type', 'patient', 'doctor', 'visit')
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self, *args, **kwargs):
        q = super(ResultViewSet, self).get_queryset(*args, **kwargs)
        return q
    
    def create(self, request):
        pass
    
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
        else:
            return super(ResultViewSet, self).list(request, *args, **kwargs)


