from crispy_forms.utils import render_crispy_form
from django.shortcuts import render, HttpResponse
import importlib
import urllib

from django.template.context_processors import csrf
from django.views import View
import json


class AjaxFormView(View):
    @staticmethod
    def get_form(data):
        klass = data.get('class', data.get('klass', False))
        if not klass:
            return False
        m = importlib.import_module(data['module'])
        form_class = getattr(m, klass)
        return form_class

    def get(self, *args, **kwargs):
        form_class = self.get_form(self.request.GET)
        if not form_class:
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        if 'id' in self.request.GET:
            form = form_class(instance=form_class._meta.model.objects.get(id=self.request.GET['id']))
        else:
            data = self.request.GET['data'] if 'data' in self.request.GET else {}
            form = form_class(initial=data)
        ctx = {}
        ctx.update(csrf(self.request))
        form_html = render_crispy_form(form, context=ctx)
        return HttpResponse(json.dumps({'success': True, 'form_html': form_html}), content_type='application/json')

    def post(self, *args, **kwargs):
        form_class = self.get_form(self.request.POST)
        if not form_class:
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        ctx = {}
        ctx.update(csrf(self.request))
        if not 'data' in self.request.POST:
            data = self.request.POST
        else:
            data = self.request.POST['data']
            try:
                data = json.loads(data)
                data = {d['name']: d['value'] for d in data}
            except:
                data = {p[0]: urllib.unquote(str(p[1])).decode('utf8') for p in [par.split('=') for par in data.split('&')]}
        if 'id' in data:
            if self.request.FILES:
                form = form_class(data=data, files=self.request.FILES, instance=form_class._meta.model.objects.get(id=data['id']))
            else:
                form = form_class(data=data, instance=form_class._meta.model.objects.get(id=data['id']))
        else:
            if self.request.FILES:
                form = form_class(data=data, files=self.request.FILES)
            else:
                form = form_class(data=data)
        if form.is_valid():
            if self.request.POST.get('user', None):
                form.save(self.request.user)
            else:
                form.save()
            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
        else:
            form_html = render_crispy_form(form, context=ctx)
            return HttpResponse(json.dumps({'success': False, 'form_html': form_html}), content_type='application/json')
