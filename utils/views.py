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
        klass = data.get('class', False)
        if not klass:
            return False
        m = importlib.import_module(data['module'])
        form_class = getattr(m, data['class'])
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
        data = self.request.POST['data']
        if type(data) == unicode:
            data = {p[0]: unicode(urllib.unquote(p[1])) for p in [par.split('=') for par in data.split('&')]}
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
