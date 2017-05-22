from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic.base import View
from timetable.models import Term
from user_profile.models import Doctor


class CalendarView(View):

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        return render(request, 'timetable/www_calendar.html', {'doctors': doctors})

    def post(self, request, *args, **kwargs):
        pass


def term_cancel_view(request):
    if not 'id' in request.POST:
        return HttpResponse(status=400)
    t = Term.objects.get(id=request.POST['id'])
    if 'cancel' in request.POST:
        t.status = 'CANCELLED'
    else:
        t.status = 'FREE'
        t.patient = None
    t.save()
    return HttpResponse(status=200)
