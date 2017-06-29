# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from timetable.models import Term
from user_profile.models import Doctor
import json


class CalendarView(View):

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        return render(request, 'timetable/www_calendar.html', {'doctors': doctors})

    def post(self, request, *args, **kwargs):
        pass


def term_cancel_view(request):
    if not 'id' in request.POST:
        return HttpResponse(status=400)
    t = Term.objects.get(id=request.POST['id'])
    if 'cancel' in request.POST:
        t.status = 'CANCELLED'
    else:
        t.status = 'FREE'
        t.patient = None
    t.save()
    return HttpResponse(status=200)


def term_move_view(request):
    if not 'id' in request.POST:
        return HttpResponse(status=400)
    t = Term.objects.get(id=request.POST['id'])
    t2 = False
    try:
        t2 = Term.objects.get(datetime=request.POST['datetime'], doctor=t.doctor)
    except:
        pass
    if t2 and (t2.patient and t.patient):
        return HttpResponse(json.dumps({'message': 'Na ten termin jest już zapisany pacjent.'}), status=400)
    if t2 and not t2.patient:
        t2.patient = t.patient
        t2.save()
    else:    
        t.datetime = request.POST['datetime']
        t.save()
    return HttpResponse(status=200)

