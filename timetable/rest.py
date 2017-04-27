from django.conf import settings
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Term
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

    def get_queryset(self):
        if 'next_visits' in self.request.GET:
            return super(TermViewSet, self).get_queryset().filter(datetime__gte=datetime.datetime.now(), status='PENDING').\
                order_by('datetime')[0:5]
        end = datetime.datetime.strptime(self.request.query_params['end'], '%Y-%m-%d')
        doctor = self.request.user.doctor
        if settings.GENERATE_TERMS and (not doctor.terms_generated_till or doctor.terms_generated_till < end.date()):
            Term.create_terms_for_period(doctor,
                                         datetime.datetime.strptime(self.request.query_params['start'], '%Y-%m-%d'),
                                         end)
        q = super(TermViewSet, self).get_queryset()
        if 'start' in self.request.GET:
            q = q.filter(datetime__gte=self.request.query_params['start'], datetime__lte=self.request.query_params['end'])
            if hasattr(self.request.user, 'doctor'):
                q = q.filter(doctor=self.request.user.doctor)
        return q



