import json
import os

import datetime
from django.conf.urls import url, include
from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from rest_framework import serializers, viewsets

from user_profile.models import Patient
from visit.models import Visit
from .models import Result
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.response import Response


# Serializers define the API representation.
class ResultSerializer(serializers.HyperlinkedModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    class Meta:
        model = Result
        fields = ('id', 'name', 'description', 'file', 'patient')


# ViewSets define the view behavior.
class ResultViewSet(viewsets.ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    filter_fields = ('type', 'patient', 'doctor', 'visit')
    filter_backends = (DjangoFilterBackend,)
    # pagination_class = None

    def get_queryset(self, *args, **kwargs):
        q = super(ResultViewSet, self).get_queryset(*args, **kwargs)
        if not 'endoscope' in self.request.GET:
            q = q.exclude(name='')
        if 'pesel' in self.request.GET:
            q = q.filter(patient__pesel=self.request.GET['pesel'])
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
            return super(ResultViewSet, self).create(request)

    def retrieve(self, request, *args, **kwargs):
        pass

    def list(self, request, *args, **kwargs):
        #if not 'pesel' in request.GET:
        #    return HttpResponseBadRequest()
        return super(ResultViewSet, self).list(request, *args, **kwargs)


