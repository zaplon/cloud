import json
import os

import datetime
from django.conf.urls import url, include
from django.db.models import Q, Sum
from django.http import HttpResponse, HttpResponseBadRequest
from elasticsearch_dsl import Search
from rest_framework import serializers, viewsets

from g_utils.rest import SearchMixin
from user_profile.models import Patient, Doctor, Specialization, User
from visit.models import Visit
from .models import Result, ResultIndex
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    specialization = serializers.PrimaryKeyRelatedField(queryset=Specialization.objects.all())
    uploaded_by = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

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
            q = q.filter(doctor__specializations__name=self.request.GET['category'])
        return q

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_authenticated() and instance.doctor == request.user.doctor:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

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
            request.data['uploaded_by'] = self.request.user.id
            return super(ResultViewSet, self).create(request)

    def retrieve(self, request, *args, **kwargs):
        doc = ResultIndex.get(id=kwargs['pk'])
        return Response({'url': doc.url})

    def categories_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        result = queryset.values('specialization__name').order_by('specialization__name')\
            .annotate(results_sum=Sum('specialization'))
        categories = [{'name': category['specialization__name'],
                       'count': category['results_sum']} for category in result]
        return Response(categories)

    def list(self, request, *args, **kwargs):
        #if not 'pesel' in request.GET:
        #    return HttpResponseBadRequest()
        if 'as_categories' in request.GET:
            return self.categories_list(request, *args, **kwargs)
        return super(ResultViewSet, self).list(request, *args, **kwargs)


