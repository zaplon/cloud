from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Icd10, Template
import json


# Serializers define the API representation.
class IcdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Icd10
        fields = ('id', 'code', 'desc')


# ViewSets define the view behavior.
class IcdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icd10.objects.all()
    serializer_class = IcdSerializer

    def get_queryset(self):
        q = super(IcdViewSet, self).get_queryset()
        if 'search' in self.request.GET:
            term = self.request.GET['search']
            q = q.filter(Q(desc__icontains=term) | Q(code__icontains=term))
        if 'exclude' in self.request.GET:
            q = q.exclude(id__in=json.loads(self.request.GET['exclude']))
        return q


class TemplateSerializer(serializers.ModelSerializer):
    tab_name = CharField(source='tab.name')
    class Meta:
        model = Template
        fields = ('text', 'tab', 'key', 'name', 'tab_name')


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer
    pagination_class = None

    def get_queryset(self):
        q = super(TemplateViewSet, self).get_queryset()
        #q = q.filter(doctor__user=self.request.user)
        if self.request.GET.get('tab', None):
            q = q.filter(tab__id=self.request.GET['tab'])
        return q



