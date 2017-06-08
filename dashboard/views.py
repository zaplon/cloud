import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views import View
from wkhtmltopdf.views import PDFTemplateView
from django.conf import settings
from user_profile.forms import DoctorForm, UserForm
from crispy_forms.layout import Layout, Div, Submit, Field
from timetable.models import Specialization, Localization
from user_profile.models import Doctor
from user_profile.rest import DoctorSerializer


@login_required
def index_view(request):
    for m in settings.MODULES:
        if type(m[0]) == list:
            if request.user.has_perms(m[0][0]) or request.user.has_perms(m[0][1]):
                return redirect('/' + m[1] + '/')
        else:
            if m[0] is True or request.user.has_perms(m[0]):
                return redirect('/' + m[1] + '/')


@login_required
def calendar_view(request):
    if not hasattr(request.user, 'doctor'):
        return render(request, 'dashboard/calendar.html')
    else:
        doctors = Doctor.objects.all()
        specializations = Specialization.objects.all()
        localizations = Localization.objects.all()
        return render(request, 'dashboard/full_calendar.html', {'doctors': doctors, 'localizations': localizations, 'specializations': specializations})

@login_required
def patients_view(request):
    return render(request, 'dashboard/patients.html')


@login_required
def archive_view(request):
    return render(request, 'dashboard/archive.html', {'USE_ELO': settings.USE_ELO})


@login_required
def icd10_view(request):
    return render(request, 'dashboard/icd10.html')


@login_required
def medicines_view(request):
    return render(request, 'dashboard/medicines.html')


class PdfView(PDFTemplateView):
    def get(self, request, *args, **kwargs):
        self.template_name = 'pdf/' + request.GET.get('template_name', 'no-pdf.html')
        self.filename = request.GET.get('filename', 'result.pdf')
        return super(PDFTemplateView, self).get(request, *args, **kwargs)


class SetupView(View):
    user_form_layout = Layout(
        Field('first_name', css_class='form-control', wrapper_class='row'),
        Field('last_name', css_class='form-control', wrapper_class='row'),
        Field('email', css_class='form-control', wrapper_class='row'),
        Field('mobile', css_class='form-control', wrapper_class='row'),
        Div(
            Div(
                Submit('save_changes', 'Zapisz', css_class="btn-primary"),
                # Submit('cancel', 'Cancel'),
                css_class='offset-sm-2 col-sm-10'
            ),
            css_class='form-group row'
        )
    )
    doctor_form_layout = Layout(
        Field('title', css_class='form-control', wrapper_class='row'),
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

    def get(self, request, *args, **kwargs):
        step = int(kwargs.get('step'))
        if step == 1:
            if hasattr(request.user, 'doctor'):
                user = self.request.user
                doctor = user.doctor
                form = DoctorForm(
                    initial={'first_name': user.first_name, 'last_name': user.last_name, 'pwz': doctor.pwz,
                             'email': user.email, 'mobile': doctor.mobile, 'title': doctor.title, 'doctor': doctor})
                form.helper.layout = self.doctor_form_layout
                c = {'form': form}
                c.update(csrf(request))
            else:
                form = UserForm(initial={'email': request.user.email, 'mobile': request.user.profile.mobile})
                form.helper.layout = self.user_form_layout
                c = {'form': form}
                c.update(csrf(request))
            return render_to_response('dashboard/setup/step_1.html', c)
        if step == 2:
            return render_to_response('dashboard/setup/step_2.html',
                                      {'doctor_data': json.dumps(DoctorSerializer(instance=request.user.doctor).data)})

    def post(self, request, *args, **kwargs):
        step = int(kwargs.get('step'))
        if step == 1:
            if hasattr(request.user, 'doctor'):
                form = DoctorForm(request.POST)
                form.helper.layout = self.doctor_form_layout
            else:
                form = UserForm(request.POST)
                form.helper.layout = self.user_form_layout
            if form.is_valid():
                form.save(request.user)
                return HttpResponseRedirect('/')
            else:
                c = {'form': form}
                c.update(csrf(request))
                return render_to_response('dashboard/setup/step_1.html', c)
