# -*- coding: utf-8 -*-
import zipfile
from xml.dom import minidom

from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from .forms import *
from g_utils.forms import ajax_form_validate
from django.views.generic.edit import CreateView, UpdateView, DeleteView
import json
from .models import Doctor, PrescriptionNumber
from django.contrib.auth.models import User


class SettingsView(View):
    template_name = 'user_profile/doctor/settings.html'

    def get_form(self):
        if hasattr(self.request.user, 'doctor'):
            doctor = self.request.user.doctor
            user = self.request.user
            form = DoctorForm(initial={'first_name': user.first_name, 'last_name': user.last_name, 'pwz': doctor.pwz,
                        'email': user.email, 'mobile': doctor.mobile, 'title': doctor.title, 'doctor': doctor})
            return form
        else:
            user = self.request.user
            form = UserForm(initial={'first_name': user.first_name, 'last_name': user.last_name,
                        'email': user.email, 'mobile': user.profile.mobile})
            return form

    def get(self, request, *args, **kwargs):
        if not hasattr(self.request.user, 'doctor'):
            self.template_name = 'user_profile/default/settings.html'
        return render(request, self.template_name, {'profile_form': self.get_form(), 'system_form': SystemForm()},
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
                    if 'dayChecked' in day and day['on']:
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
        if tab == '3':
            res = ajax_form_validate(request.POST['data'], SystemForm)
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


class AddPrescriptionNumbersView(APIView):
    queryset = PrescriptionNumber.objects.all()

    def post(self, request):
        if request.FILES['file'].name.find('.xmz') > 0:
            source = zipfile.ZipFile(request.FILES['file']).read(request.FILES['file'].name[0:-3] + 'xml')
        else:
            source = request.FILES['file'].read()
        try:
            xml = minidom.parseString(source)
        except:
            return Response(status=400, data=u'Błąd przetwarzania pliku.')

        # node = xml.getElementsByTagName('lekarz')
        doctor = self.request.user.doctor
        ns = xml.getElementsByTagName('n')
        if not ns:
            ns = xml.getElementsByTagName('recepta')
        if not ns:
            return Response(status=400, data=u'Brak numerów recept do zaimportowania.')
        for n in ns:
            try:
                val = n.childNodes[0].nodeValue
            except:
                val = n.attributes['numer'].value
            try:
                PrescriptionNumber.objects.get(nr=val)
            except:
                r = PrescriptionNumber(doctor=doctor, nr=val)
                r.save()
        return Response(status=200, data={
            'available': PrescriptionNumber.available(doctor),
            'total': PrescriptionNumber.total(doctor)}, content_type='application/json')
