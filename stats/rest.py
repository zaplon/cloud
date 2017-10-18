from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.db.models.functions import ExtractHour
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions
from datetime import datetime
from datetime import timedelta

from timetable.models import Term
from user_profile.models import Doctor, Specialization
from visit.models import Visit


class Stats(APIView):
    """
    View to list all users in the system.

    * Only admin users are able to access this view.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format=None):
        if 'type' not in request.GET:
            return Response(status=400)
        type = request.GET.get('type')
        all = type == 'all'
        all_res = {}
        from_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=30)
        if type == 'visits' or all:
            q = Visit.objects.annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id')).values(
                'month', 'c').order_by('month')
            q = list(q)
            res = {'labels': [r['month'].strftime('%m-%Y') for r in q], 'data': [r['c'] for r in q]}
            if all:
                all_res['visits'] = res
            else:
                return Response(res)
        if type == 'visits_time' or all:
            q = Term.objects.annotate(hour=ExtractHour('datetime')).values('hour').annotate(c=Count('id')).values(
                'hour', 'c')
            q = list(q)
            res = {'labels': [r['hour'] for r in q], 'data': [r['c'] for r in q]}
            if all:
                all_res['visits_time'] = res
            else:
                return Response(res)

        if type == 'doctors' or all:
            from_date = datetime.now() - timedelta(days=30)
            q = Doctor.objects.filter(terms__datetime__gte=from_date).annotate(c=Count('terms__id')).order_by('-c')[0:20]
            q = list(q)
            res = {'labels': [str(r) for r in q], 'data': [r.c for r in q]}
            if all:
                all_res['doctors'] = res
            else:
                return Response(res)
        if type == 'types' or all:
            q = Specialization.objects.filter(doctors__terms__datetime__gte=from_date,
                                              doctors__terms__patient__isnull=False).annotate(c=Count('id'))
            q = list(q)
            res = {'labels': [str(r) for r in q], 'data': [r.c for r in q]}
            if all:
                all_res['types'] = res
            else:
                return Response(res)

        return Response(all_res)
