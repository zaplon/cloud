from rest_framework import serializers, viewsets

from g_utils.rest import SearchMixin
from examination.models import Examination


class ExaminationSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')

    class Meta:
        model = Examination
        fields = ['id', 'name', 'category']


class ExaminationViewSet(SearchMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Examination.objects.filter(is_active=True)
    serializer_class = ExaminationSerializer
