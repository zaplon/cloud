from django.conf.urls import url, include
from django.db.models import Q
from rest_framework import serializers, viewsets
from rest_framework.fields import CharField
from .models import Medicine, MedicineParent, Refundation, Prescription
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

    def get_queryset(self):
        q = super(MedicineParentViewSet, self).get_queryset()
        search = None
        if 'query' in self.request.GET:
            search = self.request.GET['query']
        if 'search' in self.request.GET:
            search = self.request.GET['search']
        if search:
            q = q.filter(name__icontains=search) | q.filter(composition__icontains=search)
        return q


# Serializers define the API representation.
class MedicineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Medicine
        fields = '__all__'


# ViewSets define the view behavior.
class MedicineViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_fields = ('parent', )


# Serializers define the API representation.
class RefundationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refundation
        fields = ('to_pay', 'recommendations', 'other_recommendations')


# ViewSets define the view behavior.
class RefundationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Refundation.objects.all()
    serializer_class = RefundationSerializer
    pagination_class = None

    def get_queryset(self):
        q = super(RefundationViewSet, self).get_queryset()
        search = None
        if 'query' in self.request.GET:
            search = self.request.GET['query']
        if 'search' in self.request.GET:
            search = self.request.GET['search']
        if search:
            q = q.filter(ean=search)
        return q


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'


# ViewSets define the view behavior.
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer