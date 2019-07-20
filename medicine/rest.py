from rest_framework import viewsets

from g_utils.rest import SearchMixin
from medicine.serializers import *


class MedicineParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicineParent
        fields = '__all__'
    children = MedicineSerializer(write_only=True, many=True)

    def __init__(self, *args, **kwargs):
        super(MedicineParentSerializer, self).__init__(*args, **kwargs)
        if 'request' in kwargs['context']:
            self.user = kwargs['context']['request'].user
        else:
            self.user = None

    def create(self, validated_data):
        children = validated_data.pop('children')
        validated_data['user_id'] = self.user.id
        instance = super(MedicineParentSerializer, self).create(validated_data)
        for c in children:
            c.update({'parent': instance, 'in_use': True})
            Medicine.objects.create(**c)
        return instance

    def update(self, instance, validated_data):
        children = validated_data.pop('children')
        validated_data['user_id'] = self.user.id
        instance = super(MedicineParentSerializer, self).update(instance, validated_data)
        for c in children:
            c['parent'] = instance
            Medicine.objects.update_or_create(id=c.get('id', 0), defaults=c)
        return instance


# ViewSets define the view behavior.
class MedicineParentViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = MedicineParent.objects.filter(in_use=True)
    serializer_class = MedicineParentSerializer
    lookup_field = 'pk'

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


# ViewSets define the view behavior.
class MedicineViewSet(viewsets.ModelViewSet):
    queryset = Medicine.objects.all()
    serializer_class = MedicineSerializer
    filter_fields = ('parent', )

    def get_queryset(self):
        q = super(MedicineViewSet, self).get_queryset()
        if 'parent_name' in self.request.GET:
            q = q.filter(parent__name=self.request.GET['parent_name'])
        return q


# ViewSets define the view behavior.
class RefundationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Refundation.objects.all()
    serializer_class = RefundationSerializer
    filter_fields = ('medicine', )
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


# ViewSets define the view behavior.
class PrescriptionViewSet(viewsets.ModelViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return PrescriptionListSerializer
        if self.action == 'retrieve':
            return PrescriptionRetrieveSerializer
        return self.serializer_class

    def get_queryset(self):
        q = super(PrescriptionViewSet, self).get_queryset()
        return q.filter(doctor=self.request.user.doctor)
