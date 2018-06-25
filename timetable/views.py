# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from rest_framework.views import APIView

from timetable.models import Term
from user_profile.models import Doctor
import json


class CalendarView(View):

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        return render(request, 'timetable/www_calendar.html', {'doctors': doctors})

    def post(self, request, *args, **kwargs):
        pass


class TermCancelView(APIView):
    queryset = Term.objects.all()

    def post(self, request):
        if not 'id' in request.data:
            return HttpResponse(status=400)
        t = Term.objects.get(id=request.data['id'])
        if 'cancel' in request.data:
            t.status = 'CANCELLED'
        else:
            t.status = 'FREE'
            t.patient = None
        t.save()
        return HttpResponse(status=200)


class TermMoveView(APIView):
    queryset = Term.objects.all()

    def post(self, request):
        if not 'id' in request.data:
            return HttpResponse(status=400)
        t = Term.objects.get(id=request.data['id'])
        t2 = False
        try:
            t2 = Term.objects.get(datetime=request.data['datetime'], doctor=t.doctor)
        except:
            pass
        if t2 and (t2.patient and t.patient):
            return HttpResponse(json.dumps({'message': 'Na ten termin jest już zapisany pacjent.'}), status=400, content_type='application/json')
        if t2 and not t2.patient:
            t2.patient = t.patient
            t2.status = 'PENDING'
            t2.service = t.service
            t.service = None
            t.patient = None
            t.status = 'FREE'
            t.save()
            t2.save()
        else:
            t.datetime = request.data['datetime']
            t.save()
        return HttpResponse(status=200)

