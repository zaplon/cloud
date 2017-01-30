from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Medicine, MedicineParent
import datetime


# Serializers define the API representation.
class MedicineParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineParent
        fields = '__all__'


# ViewSets define the view behavior.
class MedicineParentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MedicineParent.objects.all()
    serializer_class = MedicineParentSerializer


# Serializers define the API representation.
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


# ViewSets define the view behavior.
class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer

