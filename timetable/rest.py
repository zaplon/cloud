from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Term
import datetime


# Serializers define the API representation.
class TermSerializer(serializers.HyperlinkedModelSerializer):
    start = CharField(source='datetime')
    end = CharField(source='get_end')
    text = CharField(source='get_title')
    className = CharField(source='status')
    class Meta:
        model = Term
        fields = ('patient', 'duration', 'doctor', 'start', 'end', 'text', 'className')


# ViewSets define the view behavior.
class TermViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_queryset(self):
        q = super(TermViewSet, self).get_queryset()
        if 'start' in self.request.GET:
            q = q.filter(datetime__gte=self.request.query_params['start'], datetime__lte=self.request.query_params['end'])
            if hasattr(self.request.user, 'doctor'):
                q = q.filter(doctor=self.request.user.doctor)
        return q



