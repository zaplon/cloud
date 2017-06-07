import json

from django.shortcuts import render, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView

from result.models import Result
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from result.forms import *
from result.search import *


class ResultCreateView(CreateView):
    model = Result
    form_class = ResultModelForm
    template_name = 'result/form.html'

    def get_context_data(self, **kwargs):
        context = super(ResultCreateView, self).get_context_data(**kwargs)
        if self.request.user and self.request.user.doctor:
            form = context['form']
            form.fields['doctor'].widget = HiddenInput()
            form.fields['doctor'].initial = self.request.user.doctor.id
        return context


class ResultDetailView(DetailView):
    model = Result
    template_name = 'result/form.html'


class ResultUpdateView(UpdateView):
    model = Result
    form_class = ResultModelForm
    template_name = 'result/form.html'

    def get_context_data(self, **kwargs):
        context = super(ResultUpdateView, self).get_context_data(**kwargs)
        if self.request.user and self.request.user.doctor:
            form = context['form']
            form.fields['doctor'].widget = HiddenInput()
            form.fields['doctor'].initial = self.request.user.doctor.id
        return context


class ResultDeleteView(DeleteView):
    model = Result
    success_url = reverse_lazy('archive')
    template_name = 'confirm_delete.html'


def search_view(request):
    if 'search' not in request.GET:
        return HttpResponse(status=400)
    search_results, search_suggestions = search(request.GET['search'])
    total = search_results.hits.total
    if total == 0:
        return HttpResponse(json.dumps({'results': [], 'count': 0, 'suggestions': search_suggestions}), content_type='application/json')
    res = {'results': [r.__dict__['_d_'] for r in search_results.hits][int(request.GET.get('offset', 0)):int(request.GET.get('limit', 10))],
           'count': total, 'suggestions': search_suggestions}
    return HttpResponse(json.dumps(res), content_type='application/json')
