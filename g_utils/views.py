# -*- coding: utf-8 -*-
import datetime
import os

from crispy_forms.helper import FormHelper
from crispy_forms.utils import render_crispy_form
from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin
from django.shortcuts import render, HttpResponse
import importlib

from django.template.context_processors import csrf
import json
import re
import urllib
from django.conf import settings
from rest_framework.views import APIView
from wkhtmltopdf.views import PDFTemplateView

from result.utils import save_document
from user_profile.models import SystemSettings


class AjaxFormView(APIView):
    permission_classes = []

    def add_data(self, data):
        if self.request.user.is_authenticated():
            if not 'user' in data:
                data['user'] = self.request.user
        data['ajax'] = True
        return data

    @staticmethod
    def render_form(form, ctx):
        helper = FormHelper(form)
        if ctx.get('read_only', False):
            helper.field_template = 'form/span_field.html'
        if getattr(form, 'horizontal', False):
            helper.wrapper_class = 'row'
            helper.label_class = 'col-md-3'
            helper.field_class = 'col-md-9'
        return render_crispy_form(form, context=ctx, helper=helper)

    @staticmethod
    def get_form(data):
        klass = data.get('class', data.get('klass', False))
        if not klass:
            return False
        m = importlib.import_module(data['module'])
        form_class = getattr(m, klass)
        return form_class

    def check_permissions(self, form_class):
        if hasattr(form_class, 'required_permission'):
            if not self.request.user.has_perm(form_class.required_permission):
                raise PermissionError('User has no permissions to use %s form' % form_class)

    def get(self, *args, **kwargs):
        form_class = self.get_form(self.request.GET)
        if not form_class:
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        try:
            self.check_permissions(form_class)
        except PermissionError:
            return HttpResponse(status=403)
        if 'id' in self.request.GET:
            form = form_class(instance=form_class._meta.model.objects.get(id=self.request.GET['id']))
        else:
            data = json.loads(self.request.GET['data']) if 'data' in self.request.GET else {}
            data = self.add_data(data)
            form = form_class(initial=data)
        ctx = {}
        ctx.update(csrf(self.request))
        ctx['read_only'] = self.request.GET.get('read_only')
        form_html = self.render_form(form, ctx)
        return HttpResponse(json.dumps({'success': True, 'form_html': form_html}), content_type='application/json')

    def post(self, *args, **kwargs):
        post_data = json.loads(self.request.body)
        form_class = self.get_form(post_data)
        if not form_class:
            return HttpResponse(json.dumps({'success': False}), content_type='application/json')
        try:
            self.check_permissions(form_class)
        except PermissionError:
            return HttpResponse(status=403)
        ctx = {}
        ctx.update(csrf(self.request))
        data = post_data['data']
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
            if 'user' in form.fields or getattr(form_class, 'save_with_user', False):
                res = form.save(user=self.request.user)
            else:
                res = form.save()
            if getattr(form, 'return_result', False):
                return HttpResponse(json.dumps({'success': True, 'result': res}), content_type='application/json')
            else:
                return HttpResponse(json.dumps({'success': True}), content_type='application/json')
        else:
            form_html = self.render_form(form, ctx)
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


class PDFView(APIView, PDFTemplateView):
    data = {}

    def post(self, request, *args, **kwargs):
        self.data = json.loads(self.request.body)
        self.template_name = 'pdf/%s.html' % self.data['template_name']
        res = super(PDFView, self).get(request, *args, **kwargs)
        name = datetime.datetime.now().strftime('%s') + '.pdf'
        file_name = os.path.join(settings.MEDIA_ROOT, 'tmp', 'pdf', name)
        f = open(file_name, 'wb')
        res.render()
        f.write(res.content)
        f.close()
        save_document(self.data['name'], self.data['patient']['id'], file_name, request.user)
        return HttpResponse(settings.MEDIA_URL + 'tmp/pdf/' + name)

    def get_context_data(self, **kwargs):
        context = self.data
        context['user'] = self.request.user
        settings = SystemSettings.objects.first()
        context['header_left'] = settings.documents_header_left
        context['header_right'] = settings.documents_header_right
        return context
