from django.shortcuts import render
from result.models import Result


class ResultCreateView(CreateView):
    model = Result
    form_class = ResultModelForm
    template_name = 'result/form.html'
