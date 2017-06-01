from django.shortcuts import render, HttpResponse
from result.models import Result
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from result.forms import *
from result.search import *


class ResultCreateView(CreateView):
    model = Result
    form_class = ResultForm
    template_name = 'result/form.html'

    
def search_view(request):
    if not 'q' in request.GET:
        return HttpResponse(status=400)
    res = search(request.GET['q'])
    return HttpResponse(res, content_type='application/json')
