# -*- coding: utf-8 -*-
from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from .forms import *
from utils.forms import ajax_form_validate
from django.views.generic.edit import CreateView, UpdateView, DeleteView
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
        return render(request, self.template_name, {'profile_form': self.get_form()},
                      content_type='text/html; charset=utf-8')

    def post(self, request):
        if not request.POST.get('tab', None):
            return HttpResponse('', status=400, content_type='application/json')
        tab = request.POST['tab']
        if tab == '1':
            doctor = request.user.doctor
            errors = None
            minimum = '20:00:00'
            maximum = '00:00:00'
            change_range = False
            for day in json.loads(request.POST['days']):
                f = HoursForm({'start': day['start'], 'end': day['end'], 'break_start': day['break_start'],
                               'break_end': day['break_end']})
                if not f.is_valid():
                    if not errors:
                        errors = {}
                    errors[day['dayIndex']] = f.errors
                else:
                    if day['dayChecked']:
                        change_range = True
                        if day['end'] > maximum:
                            maximum = day['end']
                        if day['start'] < minimum:
                            minimum = day['start']
            if not errors:
                if change_range:
                    doctor.terms_start = minimum
                    doctor.terms_end = maximum
                doctor.working_hours = request.POST['days']
                doctor.save()
                return HttpResponse(json.dumps({'success': True}), status=200, content_type='application/json')
            else:
                return HttpResponse(json.dumps({'success': False, 'errors': errors}), status=200, content_type='application/json')
        if tab == '2':
            res = ajax_form_validate(request.POST['data'], DoctorForm)
            return HttpResponse(res, status=200, content_type='application/json')


class PatientCreateView(CreateView):
    model = Patient
    form_class = PatientModelForm
    template_name = 'user_profile/patient/form.html'


class PatientUpdateView(UpdateView):
    model = Patient
    form_class = PatientModelForm
    template_name = 'user_profile/patient/form.html'


class PatientDeleteView(DeleteView):
    model = Patient
    success_url = reverse_lazy('patients')
    template_name = 'confirm_delete.html'
