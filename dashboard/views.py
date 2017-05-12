import json

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views import View
from wkhtmltopdf.views import PDFTemplateView
from django.conf import settings
from user_profile.forms import DoctorForm
from crispy_forms.layout import Layout, Div, Submit, Field

from user_profile.rest import DoctorSerializer


@login_required
def calendar_view(request):
    return render(request, 'dashboard/calendar.html')


@login_required
def patients_view(request):
    return render(request, 'dashboard/patients.html')


@login_required
def archive_view(request):
    return render(request, 'dashboard/archive.html', {'USE_ELO': settings.USE_ELO})


@login_required
def icd10_view(request):
    return render(request, 'dashboard/icd.html')


@login_required
def medicines_view(request):
    return render(request, 'dashboard/medicines.html')


class PdfView(PDFTemplateView):

    def get(self, request, *args, **kwargs):
        self.template_name = 'pdf/' + request.GET.get('template_name', 'no-pdf.html')
        self.filename = request.GET.get('filename', 'result.pdf')
        return super(PDFTemplateView, self).get(request, *args, **kwargs)


class SetupView(View):

    def get(self, request, *args, **kwargs):
        step = int(kwargs.get('step'))
        if step == 1:
            form = DoctorForm(initial={'email': request.user.email})
            form.helper.layout = Layout(
                 Field('first_name', css_class='form-control', wrapper_class='row'),
                 Field('last_name', css_class='form-control', wrapper_class='row'),
                 Field('email', css_class='form-control', wrapper_class='row'),
                 Field('mobile', css_class='form-control', wrapper_class='row'),
                 Field('pwz', css_class='form-control', wrapper_class='row'),
                 Div(
                     Div(
                         Submit('save_changes', 'Zapisz', css_class="btn-primary"),
                         # Submit('cancel', 'Cancel'),
                         css_class='offset-sm-2 col-sm-10'
                     ),
                     css_class='form-group row'
                 )
            )
            c = {'form': form}
            c.update(csrf(request))
            return render_to_response('dashboard/setup/step_1.html', c)
        if step == 2:
            return render_to_response('dashboard/setup/step_2.html',
                                      {'doctor_data': json.dumps(DoctorSerializer(instance=request.user.doctor).data)})

    def post(self, request, *args, **kwargs):
        step = int(kwargs.get('step'))
        if step == 1:
            form = DoctorForm(request.POST)
            if form.is_valid():
                form.save(request.user)
                return HttpResponseRedirect('/')
            else:
                c = {'form': form}
                c.update(csrf(request))
                return render_to_response('dashboard/setup/step_1.html', c)
