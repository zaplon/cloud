import json

import re

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, render_to_response
from django.template.loader import render_to_string
from django.views.generic import View
from wkhtmltopdf import convert_to_pdf
from wkhtmltopdf.views import PDFTemplateView
from .settings import *
from django.conf import settings
import os
import datetime
from django.conf import settings
import codecs
from .models import Form


@login_required
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
            form = ('/assets/forms/forms/' + (form + '.html'))
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
            # width on print should be less
            # w = re.search('width:(.*)px', text)
            # if w:
            #     w = w.group(0).replace(' ', '')[6:-2].strip()
            #     print_w = float(w) - 20
            #     if print_w > 100:
            #         text = text.replace(w, str(print_w))
            if text.find('type="text"') > -1:
                return text
            klass = re.search('class="([^"]+)"', text)
            klass = klass.group(1).strip() if klass else ''
            if (text.find('checkbox') > -1 or text.find('radio') > -1) and text.find('checked') > -1:
                return '<span class="checkbox %s">X</span>' % klass
            elif text.find('type="number"') > -1 or text.find('type="date"') > -1:
                value = re.search('value="(.*)"', text)
                style = re.search('style="([^"]+)"', text)
                if style:
                    style = style.group(1).strip() + 'display: inline-block;'
                else:
                    style = ''
                if value:
                    return '<span style="%s" class="%s">%s</span>' % (style, klass, value.group(1))
                else:
                    return '<span style="%s" class="%s"></span>' % (style, klass)
            else:
                return ''
        data = re.sub('<input[^>]+>', repl, data)
        data = re.sub('<.[^>]*data-ignore[^>]+>', '', data)
        data = re.sub('<.[^>]*datepicker-hide.*div>', '', data)
        print(settings.BASE_DIR + '/static')
        data = data.replace("/static", settings.BASE_DIR + '/static')
        f = codecs.open(os.path.join(settings.PROJECT_DIR, 'forms', 'templates', 'forms', 'tmp', file_name), 'w', 'utf8')
        f.write(data)
        f.close()
        return HttpResponse(json.dumps({'tmp': file_name}), content_type='application/json')


def convert_to_pdf_phantom(path, output):
    os.system('%s %s %s %s A4' %
              (os.path.join(settings.PROJECT_DIR, 'bin', 'phantomjs', 'bin', 'phantomjs'),
               os.path.join(settings.PROJECT_DIR, 'bin', 'phantomjs', 'rasterize.js'),
               path, output))


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
            if template in ['ABA', 'zgoda na znieczulenie', 'karta_badania_lekarskiego']:
                style = 'bootstrap_print.css'
            else:
                style = 'prints.css'
            css = 'file://' + os.path.join(project_dir, 'forms', 'static', 'forms', 'css', style)
            now = datetime.datetime.now().strftime('%s')
            self.filename = request.GET.get('filename', '%s_%s.pdf' % (template, now))
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
                data = convert_to_pdf('file://' + os.path.join(settings.BASE_DIR, 'forms', 'templates',
                                      self.template_name),
                                      cmd_options=self.cmd_options)
                with open(output, 'wb') as f:
                    f.write(data)
                # convert_to_pdf_phantom('file://' + os.path.join(settings.BASE_DIR, 'forms', 'templates',
                #                       self.template_name), output)
                return HttpResponse('/media/tmp/' + file_name)
            else:
                return super(PDFTemplateView, self).get(request, *args, **kwargs)
        else:
            return render_to_response(self.template_name, self.get_context_data(**kwargs))

    def get_context_data(self, **kwargs):
        {'params': self.request.GET}

