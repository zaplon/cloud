from rest_framework import serializers, viewsets

from g_utils.rest import SearchMixin
from examination.models import Examination, ExaminationCategory


class ExaminationSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Examination
        fields = ['id', 'name', 'category', 'category_name']


class ExaminationViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Examination.objects.filter(is_active=True)
    serializer_class = ExaminationSerializer


class ExaminationCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Examination
        fields = ['id', 'name']


class ExaminationCategoryViewSet(SearchMixin, viewsets.ReadOnlyModelViewSet):
    queryset = ExaminationCategory.objects.all()
    serializer_class = ExaminationCategorySerializer
