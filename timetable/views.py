from django.shortcuts import render
from django.views.generic.base import View

from user_profile.models import Doctor


class CalendarView(View):

    def get(self, request, *args, **kwargs):
        doctors = Doctor.objects.all()
        return render(request, 'timetable/www_calendar.html', {'doctors': doctors})

    def post(self, request, *args, **kwargs):
        pass
