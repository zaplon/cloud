from django.conf import settings
from django.http.response import HttpResponseBadRequest
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField

from g_utils.rest import SearchMixin
from user_profile.models import Doctor, Patient
from user_profile.rest import PatientSerializer, DoctorSerializer
from .models import Term, Service
from rest_framework.permissions import IsAuthenticated
import datetime


class TermSerializer(serializers.ModelSerializer):
    start = CharField(source='datetime')
    end = CharField(source='get_end')
    title = CharField(source='get_title')
    className = CharField(source='status')

    class Meta:
        model = Term
        fields = ('duration', 'doctor', 'start', 'end', 'title', 'className', 'status', 'id')


class TermUpdateSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())

    class Meta:
        model = Term
        fields = ('doctor', 'service', 'patient', 'status', 'duration')

    def save(self, **kwargs):
        if self.instance.status == 'FREE' and self.instance.patient:
            self.instance.status = 'PENDING'
        if self.instance.status == 'PENDING' and not self.instance.patient:
            self.instance.status = 'FREE'
        super(TermUpdateSerializer, self).save(**kwargs)


class ServiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Service
        fields = ('id', 'name')


class ServiceViewSet(viewsets.ModelViewSet, SearchMixin):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    pagination_class = None


class TermDetailSerializer(serializers.ModelSerializer):
    patient = PatientSerializer()
    service = ServiceSerializer()
    doctor = DoctorSerializer()

    class Meta:
        model = Term
        fields = ['patient', 'doctor', 'service', 'datetime', 'duration', 'id', 'status']


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'partial_update':
            return TermUpdateSerializer
        elif self.action == 'retrieve':
            return TermDetailSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        if 'next_visits' in self.request.GET:
            if hasattr(self.request.user, 'doctor'):
                return super(TermViewSet, self).get_queryset().filter(datetime__gte=timezone.now(),
                                                                      doctor=self.request.user.doctor, status='PENDING').order_by('datetime')[0:5]
            elif 'doctor' in self.request.GET:
                return super(TermViewSet, self).get_queryset().filter(datetime__gte=timezone.now(),
                                                                      doctor__id=self.request.GET['doctor'], status='PENDING').order_by('datetime')[0:5]
            elif 'doctors' in self.request.GET:
                return super(TermViewSet, self).get_queryset().filter(datetime__gte=timezone.now(),
                                                                      doctor__id__in=self.request.GET['doctors'].split(','),
                                                                      status='PENDING').order_by('datetime')[0:5]
            else:
                return Term.objects.none()
        if 'end' not in self.request.query_params:
            return super(TermViewSet, self).get_queryset()
        end = datetime.datetime.strptime(self.request.query_params['end'], '%Y-%m-%d')
        if hasattr(self.request.user, 'doctor'):
            doctor = self.request.user.doctor
        else:
            if 'doctor' not in self.request.GET:
                return Term.objects.none()
            else:
                doctor = Doctor.objects.get(id=self.request.GET['doctor'])
        if settings.GENERATE_TERMS and (not doctor.terms_generated_till or doctor.terms_generated_till < end.date()):
            Term.create_terms_for_period(doctor,
                                         datetime.datetime.strptime(self.request.query_params['start'], '%Y-%m-%d'),
                                         end)
        q = super(TermViewSet, self).get_queryset()
        if 'start' in self.request.GET:
            q = q.filter(datetime__gte=self.request.query_params['start'], datetime__lte=self.request.query_params['end'])
            q = q.filter(doctor=doctor)
        return q

