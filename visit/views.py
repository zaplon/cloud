# -*- coding: utf-8 -*-
import json
from time import sleep

from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rest_framework.views import APIView
from django.conf import settings
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from wkhtmltopdf.views import PDFTemplateView

from g_utils.utils import get_age_from_pesel, get_birth_date_from_pesel
from g_utils.views import GabinetPermissionRequiredMixin
from medicine.models import Prescription
from result.models import Result
from timetable.models import Term
from user_profile.models import SystemSettings
from visit.models import Visit, VisitTab
from .forms import *
import datetime
import os
import json
from reportlab.graphics.barcode import createBarcodeDrawing
from reportlab.lib.units import cm


class VisitView(GabinetPermissionRequiredMixin, View):
    template_name = 'visit/visit.html'
    permission_required = 'visit.change_visit'

    def get(self, request, *args, **kwargs):
        doctor = self.request.user.doctor
        term = Term.objects.get(id=kwargs['pk'])
        if not term.doctor == doctor:
            return HttpResponse(status=403)
        if not term.visit:
            visit = Visit.objects.create()
            term.visit = visit
            term.save()
        else:
            visit = term.visit
        visit.in_progress = True
        visit.save()
        tabs = visit.tabs.all()
        if len(tabs) == 0:
            tabs = visit.create_tabs()
        if len(tabs) > 0:
            tabs[0].is_active = True
        return render(request, self.template_name, {'doctor': doctor, 'tabs': tabs, 'visit': visit})

    def post(self, request, *args, **kwargs):
        term = Term.objects.get(id=kwargs['pk'])
        visit = term.visit
        doctor = self.request.user.doctor
        if not term.doctor == doctor:
            return HttpResponse(status=403)
        if request.POST.get('cancel', None):
            visit.in_progress = False
            visit.save()
            return HttpResponse(status=200)
        data = json.loads(request.POST['data'])
        tmp = self.request.POST.get('tmp', False)

        if not tmp:
            rozpoznanie = filter(lambda d: d['title'] == 'Rozpoznanie', data)
            if len(rozpoznanie) == 0 or len(rozpoznanie[0]['data']) == 0:
                return HttpResponse(json.dumps({'success': False, 'errors': {'Rozpoznanie': u'Musisz podać rozpoznanie'}}),
                                    content_type='application/json')

        for tab in data:
            vt = VisitTab.objects.get(id=tab['id'])
            vt.json = json.dumps(tab['data']) if 'data' in tab else ''
            vt.save()
            visit.tabs.add(vt)

            if vt.name == 'Leki':
                pass

        if not int(tmp):
            term.status = 'FINISHED'
            term.save()
        return HttpResponse(content=json.dumps({'success': True}), status=200, content_type='application/json')


class TemplateCreate(CreateView):
    model = Template
    form_class = TemplateForm

    def get_initial(self):
        if self.request.user.is_authenticated:
            return {'doctor': self.request.user.doctor, 'user': self.request.user}

    def get_context_data(self, **kwargs):
        context = super(TemplateCreate, self).get_context_data(**kwargs)
        tabs = Tab.objects.filter(doctor=self.request.user.doctor, parent__can_add_templates=True)
        if len(tabs) == 0:
            self.template_name = 'dashboard/section_error.html'
            context['message'] = u'Musisz najpierw dodać zakładę!'
            context['section'] = 'templates'
            return context
        return context


class TemplateUpdate(UpdateView):
    model = Template
    form_class = TemplateForm


class TemplateDelete(DeleteView):
    model = Template
    success_url = reverse_lazy('templates')
    template_name = 'confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        self.object = self.get_object()
        if not self.object.parent.template == 'default.html':
            return HttpResponse(status=400)
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class TemplateListView(ListView):

    model = Template
    template_name = 'visit/templates.html'
    queryset = Template.objects.all()

    def get_queryset(self):

        q = super(TemplateListView, self).get_queryset()
        q = q.filter(doctor=self.request.user.doctor)
        if 'orderby' in self.request.GET:
            q = q.order_by(self.request.GET['orderby'])
        return q

    def get_context_data(self, **kwargs):
        context = super(TemplateListView, self).get_context_data(**kwargs)
        return context


class TemplateDetailView(DetailView):

    model = Template

    def get_context_data(self, **kwargs):
        context = super(TemplateDetailView, self).get_context_data(**kwargs)
        return context


class TabCreate(CreateView):
    model = Tab
    form_class = TabForm

    def get_context_data(self, **kwargs):
        context = super(TabCreate, self).get_context_data(**kwargs)
        context['form'].initial['doctor'] = self.request.user.doctor
        context['form'].initial['order'] = self.request.user.doctor.tabs.count() + 1
        return context


def enable_tab(request):
    if 'id' in request.GET:
        tab = Tab.objects.get(id=request.GET['id'])
        tab.enabled = not tab.enabled
        tab.save()
        return HttpResponse(status=200)


class TabUpdate(UpdateView):
    model = Tab
    form_class = TabForm


class TabDelete(DeleteView):
    model = Tab
    success_url = reverse_lazy('tabs')
    template_name = 'confirm_delete.html'


class TabDetailView(DetailView):

    model = Tab
    template_name = 'visit/tab_detail.html'

    def get_context_data(self, **kwargs):
        context = super(TabDetailView, self).get_context_data(**kwargs)
        return context


class TabsListView(ListView):

    model = Tab
    template_name = 'visit/tabs.html'

    def get_queryset(self):
        q = super(TabsListView, self).get_queryset().filter(doctor__user=self.request.user)
        if 'orderby' in self.request.GET:
            q = q.order_by(self.request.GET['orderby'])
        return q

    def get_context_data(self, **kwargs):
        context = super(TabsListView, self).get_context_data(**kwargs)
        return context


class GabinetPdfView(APIView, PDFTemplateView):
    def get(self, request, *args, **kwargs):
        if 'as_link' in request.GET or 'to_archive' in request.GET:
            res = super(PDFTemplateView, self).get(request, *args, **kwargs)
            name = datetime.datetime.now().strftime('%s') + '.pdf'
            for i in range(0,10):
                try:
                    res.render()
                    res.content
                except:
                    sleep(1)
                else:
                    break
            if 'as_link' in request.GET:
                f = open(os.path.join(settings.MEDIA_ROOT, 'tmp', 'pdf', name), 'wb')
                f.write(res.content)
                f.close()
                return HttpResponse(settings.MEDIA_URL + 'tmp/pdf/' + name)
            else:
                visit = Visit.objects.get(id=request.GET['visit_id'])
                r = Result.objects.create(name='Wizyta', uploaded_by=request.user, visit=visit, patient=visit.term.patient,
                                      specialization=request.user.doctor.specializations.first())
                r.file.save(name, ContentFile(res.content))
                return HttpResponse(status=200)
        else:
            return super(PDFTemplateView, self).get(request, *args, **kwargs)


class PdfView(GabinetPdfView):

    def get(self, request, *args, **kwargs):
        term = Term.objects.get(id=kwargs['pk'])
        visit = term.visit
        self.visit = visit
        self.template_name = 'pdf/visit.html'
        self.filename = term.patient.__str__() + '.pdf'
        return super(PdfView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        pesel = self.visit.term.patient.pesel if self.visit.term.patient.pesel else ''
        barcode = createBarcodeDrawing('Code128', value=pesel, width=5 * cm, height=0.5 * cm)
        file_name = datetime.datetime.now().strftime('%s')
        barcode.save(formats=['png'], outDir=os.path.join(settings.MEDIA_ROOT, 'tmp', file_name), _renderPM_dpi=200)
        system_settings = SystemSettings.get_user_settings(self.request.user)
        header_left = system_settings.documents_header_left
        header_right = system_settings.documents_header_right
        patient_age = get_age_from_pesel(pesel)
        patient_birth_date = get_birth_date_from_pesel(pesel)
        prescriptions = Prescription.objects.filter(visit=self.visit, deleted__isnull=True)
        for p in prescriptions:
            p.meds = p.medicines.all()
        return {'visit': self.visit, 'IMAGES_ROOT': settings.APP_URL + 'static/', 'header_left': header_left,
                'patient': self.visit.term.patient, 'header_right': header_right,
                'patient_age': patient_age, 'patient_birth_date': patient_birth_date,
                'prescriptions': prescriptions,
                'barcode': settings.APP_URL + 'media/tmp/' + file_name + '/Drawing000.png'}
