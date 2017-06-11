from django.conf import settings
from django.http.response import HttpResponseBadRequest
from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField

from user_profile.models import Doctor
from .models import Term
from rest_framework.permissions import IsAuthenticated
import datetime


# Serializers define the API representation.
class TermSerializer(serializers.HyperlinkedModelSerializer):
    start = CharField(source='datetime')
    end = CharField(source='get_end')
    title = CharField(source='get_title')
    className = CharField(source='status')

    class Meta:
        model = Term
        fields = ('patient', 'duration', 'doctor', 'start', 'end', 'title', 'className', 'status', 'id')


# ViewSets define the view behavior.
class TermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = None

    def get_queryset(self):
        if 'next_visits' in self.request.GET:
            if hasattr(self.request.user, 'doctor'):
                return super(TermViewSet, self).get_queryset().filter(datetime__gte=timezone.now(),
                                                                      doctor=self.request.user.doctor, status='PENDING').order_by('datetime')[0:5]
            elif 'doctor' in self.request.GET:
                return super(TermViewSet, self).get_queryset().filter(datetime__gte=timezone.now(),
                                                                      doctor__id=self.request.GET['doctor'], status='PENDING').order_by('datetime')[0:5]
            else:
                return Term.objects.none()
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



