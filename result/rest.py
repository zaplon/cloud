import json
import os

import datetime

from django.db.models import Count
from django.http import HttpResponse, HttpResponseNotFound
from rest_framework import serializers, viewsets
from django_redis import get_redis_connection
from rest_framework.decorators import action

from g_utils.rest import SearchMixin
from user_profile.models import Patient, Doctor, Specialization, User
from visit.models import Visit
from .models import Result, ResultIndex
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response
from .tasks import generate_results_pdf


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    specialization = serializers.PrimaryKeyRelatedField(queryset=Specialization.objects.all())
    uploaded_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    def __init__(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['uploaded_by'] = kwargs['context'].pop('uploaded_by', None)
        super(ResultSerializer, self).__init__(*args, **kwargs)

    class Meta:
        model = Result
        fields = ('id', 'name', 'description', 'file', 'patient', 'specialization', 'uploaded_by', 'uploaded')


class ResultTableSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.CharField(source='patient.__str__')
    specialization = serializers.CharField(source='specialization.__str__')
    pesel = serializers.CharField(source='patient.pesel')

    class Meta:
        model = Result
        fields = ('id', 'name', 'description', 'file', 'uploaded', 'patient', 'specialization', 'pesel', 'description')


# ViewSets define the view behavior.
class ResultViewSet(SearchMixin, viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_fields = ('type', 'patient', 'doctor', 'visit')
    filter_backends = (DjangoFilterBackend,)
    search_filters = ['patient__pesel', 'name', 'patient__last_name', 'patient__first_name']
    # pagination_class = None

    def get_serializer_class(self):
        if 'table' in self.request.GET:
            return ResultTableSerializer
        return self.serializer_class

    def get_queryset(self, *args, **kwargs):
        q = super(ResultViewSet, self).get_queryset(*args, **kwargs)
        if not 'endoscope' in self.request.GET:
            q = q.exclude(name='')
        if 'pesel' in self.request.GET:
            q = q.filter(patient__pesel=self.request.GET['pesel'])
        if 'category' in self.request.GET:
            q = q.filter(specialization__name=self.request.GET['category'])
        return q

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated and instance.uploaded_by == request.user:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def get_serializer_context(self):
        context = super(ResultViewSet, self).get_serializer_context()
        context['uploaded_by'] = self.request.user.id
        return context

    def create(self, request):
        if 'endoscope_image' in request.POST or 'endoscope_video' in request.POST:
            r = Result()
            r.patient_id = request.POST['patient']
            r.visit = Visit.objects.get(id=request.POST['visit'])
            if 'endoscope_image' in request.POST:
                r.type = 'ENDOSCOPE_IMAGE'
                ext = 'jpg'
            else:
                r.type = 'ENDOSCOPE_VIDEO'
                ext = 'omg'
            file_name = datetime.datetime.now().strftime('%d-%m-%Y %H:%M') + '.' + ext
            path = os.path.join(settings.MEDIA_ROOT, 'results', file_name)
            f = open(path, 'wb')
            f.write(request.POST['file'])
            f.close()
            r.file.name = os.path.join('results', file_name)
            r.save()
            return HttpResponse(json.dumps({'id': r.id}), status=200, content_type='application/json')
        else:
            return super(ResultViewSet, self).create(request)

    def retrieve(self, request, *args, **kwargs):
        doc = ResultIndex.get(id=kwargs['pk'])
        return Response({'url': doc.url})

    def categories_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result = queryset.values('specialization__name').order_by('specialization__name')\
            .annotate(results_count=Count('specialization'))
        categories = [{'name': category['specialization__name'],
                       'count': category['results_count']} for category in result]
        return Response(categories)

    def list(self, request, *args, **kwargs):
        #if not 'pesel' in request.GET:
        #    return HttpResponseBadRequest()
        if 'as_categories' in request.GET:
            return self.categories_list(request, *args, **kwargs)
        return super(ResultViewSet, self).list(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def generate_pdf(self, request, *args, **kwargs):
        patient_id = request.GET['patient_id']
        period = request.GET['period']
        generate_results_pdf.delay(patient_id, period)
        return HttpResponse()

    @action(detail=False, methods=['get'])
    def get_results_pdf(self, request, *args, **kwargs):
        redis = get_redis_connection()
        pdf = redis.get(settings.RESULTS_PDF_KEY_PATTERN % (request.GET['patient_id'], request.GET['period']))
        if pdf:
            return HttpResponse(pdf)
        else:
            return HttpResponseNotFound()

    @action(detail=False, methods=['post'])
    def add_images(self, request, *args, **kwargs):
        try:
            patient_id = request.data['patient_id']
        except KeyError:
            return HttpResponse(status=400)
        for file in request.FILES.getlist('files[]'):
            r = Result()
            r.uploaded_by = self.request.user
            r.patient_id = patient_id
            r.name = request.data.get('name', 'Dokument')
            if request.data.get('category_id'):
                r.category_id = request.data['category_id']
            r.save()
            r.file.save(file.name, file.file)
        return HttpResponse()
