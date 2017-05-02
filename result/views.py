from django.shortcuts import render
from result.models import Result
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from result.forms import *


class ResultCreateView(CreateView):
    model = Result
    form_class = ResultModelForm
    template_name = 'result/form.html'
