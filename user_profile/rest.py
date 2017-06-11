from django.conf.urls import url, include
from django.db.models import Q, Min
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField, ListField, IntegerField
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.conf import settings
from .models import Doctor, Patient, Note
import datetime


# Serializers define the API representation.
class PatientSerializer(serializers.HyperlinkedModelSerializer):
    # first_name = CharField(source='user.first_name')
    # last_name = CharField(source='user.last_name')
    class Meta:
        model = Patient
        fields = ('id', 'mobile', 'first_name', 'last_name', 'pesel', 'address')


class PatientAutocompleteSerializer(serializers.ModelSerializer):
    label = CharField(source='name_with_pesel')
    value = CharField(source='name')

    class Meta:
        model = Patient
        fields = ('label', 'value', 'id')


# ViewSets define the view behavior.
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer

    def get_queryset(self):
        q = Patient.objects.all()
        if 'term' in self.request.GET:
            t = self.request.GET['term']
            q = q.filter(Q(last_name__icontains=t) | Q(first_name__icontains=t) | Q(pesel__icontains=t))
        return q

    def get_serializer_class(self):
        if 'term' in self.request.GET:
            return PatientAutocompleteSerializer
        else:
            return self.serializer_class


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
    pagination_class = None

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
        
        
class DoctorCalendarSerializer(serializers.ModelSerializer):
    first_term = serializers.DateTimeField(format=settings.DATE_FORMAT)
    class Meta:
        model = Doctor
        fields = ('id', 'name', 'first_term', 'terms_start', 'terms_end')


# ViewSets define the view behavior.
class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer

    def get_serializer_class(self):
        if 'calendar' in self.request.GET:
            return DoctorCalendarSerializer
        else:
            return self.serializer_class

    def get_queryset(self, *args, **kwargs):
        if hasattr(self.request.user, 'doctor') and 'id' not in kwargs:
            return Doctor.objects.filter(user=self.request.user)
        else:
            get_params = self.request.GET
            q = super(DoctorViewSet, self).get_queryset()
            if 'dateFrom' in get_params:
                dt = datetime.datetime.strptime(get_params['dateFrom'], '%Y-%m-%d')
            else:
                dt = datetime.datetime.today()
            if 'specialization' in get_params:
                q = q.filter(specializations__id=get_params['specialization'])
            if 'name_like' in get_params:
                q = q.filter(Q(user__first_name__icontains=get_params['name_like']) |
                             Q(user__last_name__icontains=get_params['name_like']))
            q = q.filter(terms__status='FREE', terms__datetime__gt=dt)
            q = q.annotate(first_term=Min('terms__datetime')).order_by('-first_term')
            return q


