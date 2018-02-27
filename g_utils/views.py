# -*- coding: utf-8 -*-
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.shortcuts import render, HttpResponse
import importlib
import urllib

from django.template.context_processors import csrf
from django.views import View
import json
import re
import urllib
from django.conf import settings


class AjaxFormView(View):

    def add_data(self, data):
        if self.request.user.is_authenticated():
            if not 'user' in data:
                data['user'] = self.request.user
        data['ajax'] = True
        return data

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
            data = json.loads(self.request.GET['data']) if 'data' in self.request.GET else {}
            data = self.add_data(data)
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
        data = self.add_data(data.copy())
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
            if 'user' in form.fields:
                form.save(user=self.request.user)
            else:
                form.save()
            return HttpResponse(json.dumps({'success': True}), content_type='application/json')
        else:
            form_html = render_crispy_form(form, context=ctx)
            return HttpResponse(json.dumps({'success': False, 'form_html': form_html}), content_type='application/json')


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_location_code(request):
    ['192.168.11', '192.168.4']
    ip = str(get_client_ip(request))
    if re.match("192.168.11", ip):
        return 'PDT'
    if re.match("192.168.2", ip) or re.match("192.168.1", ip) or re.match("192.168.0", ip):
        return 'WAR'
    return 'KEN'


def escape_chars(text):
    text = text.lower()
    escape_map = {'ą': 'a', 'ę': 'e', 'ł': 'l', 'ś': 's', 'ć': 'c', 'ó': 'o', 'ż': 'z', 'ź': 'z', '/':'_' }
    for e in escape_map:
        text = text.replace(e.decode('utf8'), escape_map[e])
    return text


def send_sms_code(my_code, my_mobile, username=''):
    username = escape_chars(username)
    url_text = 'https://api1.serwersms.pl/zdalnie/index.php?login=webapi_misalgabinet&haslo=tenibag123$&akcja=wyslij_sms&nadawca=SPSR-GAB&numer=%2B48' + str(
        my_mobile) + '&wiadomosc=Haslo%20dla%20'+username+':' + str(my_code) + ''
    if settings.SMS_ON:
        urllib.urlopen(url_text)


class GabinetPermissionRequiredMixin(PermissionRequiredMixin, AccessMixin):
    raise_exception = True