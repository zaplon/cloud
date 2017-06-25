from django.db.models import Count
from django.db.models.functions import TruncMonth
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import authentication, permissions

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
        if type == 'visits' or all:
            q = Visit.objects.annotate(month=TruncMonth('created')).values('month').annotate(c=Count('id')).values(
                'month', 'c').order_by('month')
            q = list(q)
            res = {'labels': [r['month'] for r in q], 'data': [r['c'] for r in q]}
            if all:
                all_res['visits'] = res
            else:
                return Response(res)
        return Response(all_res)
