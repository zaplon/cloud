import json

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
    if 'search' not in request.GET:
        return HttpResponse(status=400)
    search_results, search_suggestions = search(request.GET['search'])
    total = search_results.hits.total
    if total == 0:
        return HttpResponse(json.dumps({'results': [], 'count': 0, 'suggestions': search_suggestions}), content_type='application/json')
    res = {'results': [r.__dict__['_d_'] for r in search_results.hits][int(request.GET.get('offset', 0)):int(request.GET.get('limit', 10))],
           'count': total, 'suggestions': search_suggestions}
    return HttpResponse(json.dumps(res), content_type='application/json')
