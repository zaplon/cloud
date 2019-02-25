import json
from rest_framework.pagination import LimitOffsetPagination


class SearchMixin(object):
    search_filters = ['name']
    fields_mapping = {'name': 'name'}

    def get_queryset(self):
        q = super(SearchMixin, self).get_queryset()
        filtered_q = q.model.objects.none()
        params = self.request.query_params
        if params.get('byColumn', False) and bool(int(params['byColumn'])):
            for field, value in json.loads(params['search']).items():
                backend_field = self.fields_mapping.get(field, field)
                query_filter = backend_field + '__icontains'
                q &= q.model.objects.filter(**{query_filter: value})
        elif 'term' in params or 'search' in params:
            term = params.get('term', params.get('search'))
            for field in self.search_filters:
                query_filter = field + '__icontains'
                filtered_q |= q.model.objects.filter(**{query_filter: term})
            q = q & filtered_q
        if 'exclude' in params:
            ids_to_exclude = [id for id in params['exclude'].split(',') if id]
            if ids_to_exclude:
                q = q.exclude(id__in=params['exclude'].split(','))
        if 'term' in self.request.GET:
            self.pagination_class = None
            q = q[0:20]
        if 'orderBy' in params:
            sort_field = params['orderBy']
            order_by = self.fields_mapping.get(sort_field, sort_field)
            if 'ascending' in params and bool(int(params['ascending'])):
                q = q.order_by(order_by)
            else:
                q = q.order_by('-' + order_by)
        return q


class OnlyDoctorRecords(object):

    def get_queryset(self):
        return super(OnlyDoctorRecords, self).get_queryset().filter(doctor=self.request.user.doctor)


class GabinetPagination(LimitOffsetPagination):

    def paginate_queryset(self, queryset, request, view=None):
        if 'no_pagination' in request.query_params:
            return None
        return super().paginate_queryset(queryset, request, view)


