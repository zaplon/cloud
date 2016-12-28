from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from .models import Result


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Result
        fields = ('name', 'description', 'file')


# ViewSets define the view behavior.
class ResultViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer


