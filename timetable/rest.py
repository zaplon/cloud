from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField

from g_utils.rest import SearchMixin
from user_profile.models import Doctor, Patient
from user_profile.rest import PatientSerializer, DoctorSerializer
from .models import Term, Service, Localization
import datetime


class TermSerializer(serializers.ModelSerializer):
    start = CharField(source='datetime')
    end = CharField(source='get_end')
    title = CharField(source='get_title')
    patient = CharField(source='get_patient')
    className = CharField(source='status')

    class Meta:
        model = Term
        fields = ('duration', 'doctor', 'start', 'end', 'title', 'className', 'status', 'id', 'patient')


class TermCreateSerializer(serializers.ModelSerializer):
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all(), allow_null=True)
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all(), allow_null=True)

    class Meta:
        model = Term
        fields = ('doctor', 'service', 'patient', 'status', 'duration', 'datetime', 'id')

    def create(self, validated_data):
        try:
            instance = Term.objects.get(datetime=validated_data['datetime'], doctor=validated_data['doctor'],
                                        status='FREE')
            validated_data['status'] = 'PENDING'
            return self.update(instance, validated_data)
        except ObjectDoesNotExist:
            return super(TermCreateSerializer, self).create(validated_data)
        except MultipleObjectsReturned:
            instance = Term.objects.filter(datetime=validated_data['datetime'], doctor=validated_data['doctor'],
                                           status='FREE').first()
            return self.update(instance, validated_data)


class TermUpdateSerializer(TermCreateSerializer):

    def save(self, **kwargs):
        if self.instance.status == 'FREE' and self.validated_data['patient']:
            self.instance.status = 'PENDING'
        elif self.instance.status == 'PENDING' and not self.instance.patient:
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


class BookingSerializer(serializers.ModelSerializer):
    doctor = serializers.CharField(source='doctor.__str__')
    service = serializers.CharField(source='service.__str__')
    localization = serializers.CharField(source='localization.__str__')

    class Meta:
        model = Term
        fields = ['id', 'doctor', 'service', 'datetime', 'duration', 'status', 'localization']


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.filter(status='FREE')
    serializer_class = BookingSerializer
    filter_fields = ['doctor']

    def get_queryset(self):
        q = super(BookingViewSet, self).get_queryset()
        q = q.filter(datetime__gte=self.request.GET['start'])
        q = q.filter(doctor__service__id=self.request.GET['service'])
        return q


class TermViewSet(viewsets.ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    pagination_class = None

    def get_serializer_class(self):
        if self.action == 'create':
            return TermCreateSerializer
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
        if not doctor.working_hours:
            return Term.objects.none()
        if settings.GENERATE_TERMS and (not doctor.terms_generated_till or doctor.terms_generated_till < end.date()):
            Term.create_terms_for_period(doctor,
                                         datetime.datetime.strptime(self.request.query_params['start'], '%Y-%m-%d'),
                                         end)
        q = super(TermViewSet, self).get_queryset()
        if 'start' in self.request.GET:
            q = q.filter(datetime__gte=self.request.query_params['start'], datetime__lte=self.request.query_params['end'])
            q = q.filter(doctor=doctor)
        return q


class LocalizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Localization
        fields = '__all__'


class LocalizationViewSet(viewsets.ModelViewSet):
    queryset = Localization.objects.all()
    serializer_class = LocalizationSerializer
    pagination_class = None
