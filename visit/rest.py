from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from .models import Icd10, Template


# Serializers define the API representation.
class IcdSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Icd10
        fields = ('code', 'desc')


# ViewSets define the view behavior.
class IcdViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Icd10.objects.all()
    serializer_class = IcdSerializer

    def get_queryset(self):
        q = super(IcdViewSet, self).get_queryset()
        if 'search' in self.request.GET:
            term = self.request.GET['search']
            q = q.filter(Q(desc__icontains=term) | Q(code__icontains=term))
        return q


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = ('text', 'tab', 'key', 'name')


class TemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

    def get_queryset(self):
        q = super(TemplateViewSet, self).get_queryset()
        #q = q.filter(doctor__user=self.request.user)
        if self.request.GET.get('tab', None):
            q = q.filter(tab__id=self.request.GET['tab'])
        return q



