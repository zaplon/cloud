# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from visit.models import Template, Tab
from .forms import *


class VisitView(View):
    template_name = 'visit/visit.html'

    def get(self, request, *args, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


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

    def get_queryset(self):
        q = super(TemplateListView, self).get_queryset()
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
    fields = ['name']


class TabDelete(DeleteView):
    model = Tab
    success_url = reverse_lazy('tabs')


class TabListView(ListView):

    model = Tab
    Tab_name = 'visit/tabs.html'

    def queryset(self):
        q = super(TabListView, self).get_queryset()
        if 'orderby' in self.request.GET:
            q = q.order_by(self.request.GET['orderby'])
        return q

    def get_context_data(self, **kwargs):
        context = super(TabListView, self).get_context_data(**kwargs)
        return context


class TabDetailView(DetailView):

    model = Tab

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