from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField, ListField
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from .models import Doctor, Patient, Note
import datetime


# Serializers define the API representation.
class PatientSerializer(serializers.HyperlinkedModelSerializer):
    #first_name = CharField(source='user.first_name')
    #last_name = CharField(source='user.last_name')
    class Meta:
        model = Patient
        fields = ('id', 'mobile', 'first_name', 'last_name', 'pesel', 'address')


# ViewSets define the view behavior.
class PatientViewSet(viewsets.ModelViewSet):
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


class UserSerializer(serializers.ModelSerializer):
    can_edit_terms = serializers.SerializerMethodField('check_if_can_edit_terms')
    can_edit_visits = serializers.SerializerMethodField('check_if_can_edit_visits')

    def check_if_can_edit_terms(self, instance):
        return not instance.has_perm('timetable.change_term')

    def check_if_can_edit_visits(self, instance):
        return not instance.has_perm('visit.change_visit')

    class Meta:
        model = User
        fields = ('username', 'email', 'can_edit_terms', 'can_edit_visits')


# Serializers define the API representation.
class DoctorSerializer(serializers.HyperlinkedModelSerializer):
    name = CharField(source='get_name')
    working_hours = ListField(source='get_working_hours')
    class Meta:
        model = Doctor
        fields = ('mobile', 'pwz', 'terms_start', 'terms_end', 'name', 'id', 'working_hours')


# ViewSets define the view behavior.
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_queryset(self, *args, **kwargs):
        if self.request.user.doctor and not 'id' in kwargs:
            return Doctor.objects.filter(user=self.request.user)
        else:
            return super(DoctorViewSet, self).get_queryset()




