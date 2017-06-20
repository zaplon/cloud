import json

import re
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.views.generic import View
from wkhtmltopdf.views import PDFTemplateView
from .settings import *
from django.conf import settings
import os
import datetime
from django.conf import settings
import codecs
from .models import Form


def get_form(request):
    return render(request, 'forms/' + request.GET.get('form', 'no_form.html'))


class EditFormView(View):

    def get(self, request, *args, **kwargs):
        form = request.GET.get('form', 'no_form.html')
        template_name = form
        params = request.GET
        template = 'forms/editor.html'
        fs = Form.objects.filter(name=template_name, user=request.user).order_by('-created')
        if len(fs) > 0:
            form = '/media/' + fs[0].path
        else:
            form = ('/static/forms/forms/' + (form + '.html'))
        body = render_to_string(template, {'params': params, 'form': form,
                                           'template_name': template_name})
        return HttpResponse(body, status=200)

    def post(self, request, *args, **kwargs):
        data = request.POST.get('data', '')
        timestamp = datetime.datetime.now().strftime('%s')
        file_name = timestamp + '.html'

        if request.POST.get('tmp', False):
            # tmp html
            tmp_name = os.path.join('tmp', 'forms', file_name)
            f = codecs.open(os.path.join(settings.MEDIA_ROOT, tmp_name), 'w', 'utf8')
            f.write(data)
            Form.objects.create(name=request.POST.get('name', ''), path=tmp_name, user=request.user)
            return HttpResponse(status=200)
        data = data.replace('<textarea', '<span')
        data = data.replace('/textarea', '/span')

        def repl(m):
            text = m.group(0)
            if text.find('checkbox') > -1 and text.find('checked') > -1:
                return '<span class="checkbox">X</span>'
            elif text.find('type="text"') > -1:
                return text
            elif text.find('type="number"') > -1:
                value = re.search('value="(.*)"', text)
                if value:
                    return '<span>%s</span>' % value.group(1)
                else:
                    return '<span></span>'
            else:
                return ''
        data = re.sub('<input[^>]+>', repl, data)
        data = re.sub('<.*data-ignore.*[^>]>', '', data)
        f = codecs.open(os.path.join(settings.PROJECT_DIR, 'forms', 'templates', 'forms', 'tmp', file_name), 'w', 'utf8')
        f.write(data)
        f.close()
        return HttpResponse(json.dumps({'tmp': file_name}), content_type='application/json')


class FormView(PDFTemplateView):

    def get(self, request, *args, **kwargs):
        no_form_template = 'no_form'
        template = request.GET.get('template_name', no_form_template)
        if 'tmp' in request.GET:
            self.template_name = 'forms/tmp/' + request.GET['tmp']
        else:
            self.template_name = 'forms/' + template + '.html'
        if 'print' in request.GET:
            project_dir = settings.PROJECT_DIR
            css = 'file://' + os.path.join(project_dir, 'forms', 'static', 'forms', 'css', 'prints.css')
            print css
            self.filename = request.GET.get('filename', 'result.pdf')
            config = FORMS.get(template, FORMS['default'])
            self.cmd_options = {'page-size': config.get('page-size', 'A4'),
                                'orientation': config.get('orientation', 'Portrait'),
                                'user-style-sheet': css}
            for c in config:
                if c not in self.cmd_options:
                    self.cmd_options[c] = config[c]
            if 'as_file' in request.GET:
                file_name = datetime.datetime.now().strftime('%s') + '.pdf'
                output = os.path.join(settings.MEDIA_ROOT, 'tmp', file_name)
                self.cmd_options['output'] = output
            res = super(PDFTemplateView, self).get(request, *args, **kwargs)
            if 'as_file' in request.GET:
                HttpResponse('media/tmp' + file_name)
            else:
                return res
        else:
            return render_to_response(self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        {'params': self.request.GET}

