from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from rest_framework.response import Response
from rest_framework import status

from .models import Doctor, Patient, Note
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
class NoteSerializer(serializers.ModelSerializer):
    author = CharField(source='get_author', required=False)
    class Meta:
        model = Note
        fields = ('id', 'text', 'patient', 'doctor', 'author')


# ViewSets define the view behavior.
class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer

    def get_queryset(self):
        q = super(NoteViewSet, self).get_queryset()
        if 'patient' in self.request.GET:
            q = q.filter(patient__id= self.request.GET['patient'])
        return q

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if not request.user.is_authenticated() or not instance.doctor == request.user.doctor:
            return Response(status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



# Serializers define the API representation.
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    name = CharField(source='get_name')
    class Meta:
        model = Doctor
        fields = ('mobile', 'pwz', 'terms_start', 'terms_end', 'name', 'id')


# ViewSets define the view behavior.
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self, *args, **kwargs):
        if self.request.user.doctor and not 'id' in kwargs:
            return Doctor.objects.filter(user=self.request.user)
        else:
            return super(DoctorViewSet, self).get_queryset()




