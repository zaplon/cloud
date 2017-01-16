# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from timetable.models import Term
from visit.models import Template, Tab, Visit
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *


class VisitView(View, LoginRequiredMixin):
    template_name = 'visit/visit.html'

    def get(self, request, *args, **kwargs):
        doctor = self.request.user.doctor
        term = Term.objects.get(id=kwargs['pk'])
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
        if request.POST.get('cancel', None):
            visit = Term.objects.get(id=kwargs['pk']).visit
            visit.in_progress = False
            visit.save()
            return HttpResponse(status=200)


class TemplateCreate(CreateView):
    model = Template
    form_class = TemplateForm

    def get_context_data(self, **kwargs):
        context = super(TemplateCreate, self).get_context_data(**kwargs)
        tabs = Tab.objects.filter(doctor=self.request.user.doctor)
        if len(tabs) == 0:
            self.template_name = 'dashboard/section_error.html'
            context['message'] = u'Musisz najpierw dodać zakładę!'
            context['section'] = 'templates'
            return context
        context['form'].fields['tab'].queryset = tabs
        return context

    def post(self, request, *args, **kwargs):
        super(TemplateCreate, self).post(request, *args, **kwargs)


class TemplateUpdate(UpdateView):
    model = Template
    form_class = TemplateForm
    fields = ['name']


class TemplateDelete(DeleteView):
    model = Template
    success_url = reverse_lazy('templates')


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
        return context


class TabUpdate(UpdateView):
    model = Tab
    form_class = TabForm


class TabDelete(DeleteView):
    model = Tab
    success_url = reverse_lazy('tabs')


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
        q = super(TabsListView, self).get_queryset()
        if 'orderby' in self.request.GET:
            q = q.order_by(self.request.GET['orderby'])
        return q

    def get_context_data(self, **kwargs):
        context = super(TabsListView, self).get_context_data(**kwargs)
        return context
