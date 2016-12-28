from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Doctor, Patient
import datetime


# Serializers define the API representation.
class PatientSerializer(serializers.HyperlinkedModelSerializer):
    first_name = CharField(source='user.first_name')
    last_name = CharField(source='user.last_name')
    class Meta:
        model = Patient
        fields = ('mobile', 'first_name', 'last_name')


# ViewSets define the view behavior.
class PatientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


# Serializers define the API representation.
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Doctor
        fields = ('mobile')


# ViewSets define the view behavior.
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = PatientSerializer





