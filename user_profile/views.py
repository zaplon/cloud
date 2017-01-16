# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from django.views import View
from .forms import *
from utils.forms import ajax_form_validate
import json


class SettingsView(View):
    template_name = 'user_profile/doctor/settings.html'

    def get_form(self):
        if hasattr(self.request.user, 'doctor'):
            doctor = self.request.user.doctor
            user = self.request.user
            form = DoctorForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'pwz': doctor.pwz,
                        'email': user.email})
            return form

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, {'profile_form': self.get_form()})

    def post(self, request):
        if not request.POST.get('tab', None):
            return HttpResponse('', status=400, content_type='application/json')
        tab = request.POST['tab']
        if tab == '1':
            doctor = request.user.doctor
            errors = None
            for day in json.loads(request.POST['days']):
                f = HoursForm({'start': day['start'], 'end': day['end'], 'break_start': day['break_start'],
                               'break_end': day['break_end']})
                if not f.is_valid():
                    if not errors:
                        errors = {}
                    errors[day['dayIndex']] = f.errors
            if not errors:
                doctor.working_hours = request.POST['days']
                doctor.save()
                return HttpResponse(json.dumps({'success': True}), status=200, content_type='application/json')
            else:
                return HttpResponse(json.dumps({'success': False, 'errors': errors}), status=200, content_type='application/json')
        if tab == '2':
            res = ajax_form_validate(request.POST['data'], DoctorForm)
            return HttpResponse(res, status=200, content_type='application/json')



class PatientView():
    pass