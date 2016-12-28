from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.template.context_processors import csrf
from django.views import View
from user_profile.forms import DoctorForm


@login_required
def calendar_view(request):
    return render_to_response('dashboard/calendar.html')


@login_required
def patients_view(request):
    return render_to_response('dashboard/patients.html')


@login_required
def icd10_view(request):
    return render_to_response('dashboard/icd.html')


class SetupView(View):

    def get(self, request, *args, **kwargs):
        step = int(kwargs.get('step'))
        if step == 1:
            form = DoctorForm(initial={'email': request.user.email})
            c = {'form': form}
            c.update(csrf(request))
            return render_to_response('dashboard/setup/step_1.html', c)
        if step == 2:
            return render_to_response('dashboard/setup/step_2.html')

    def post(self, request, *args, **kwargs):
        pass