
class SearchMixin(object):
    search_filters = ['name']

    def get_queryset(self):
        q = super(SearchMixin, self).get_queryset()
        filtered_q = q.model.objects.none()
        if 'term' in self.request.GET or 'search' in self.request.GET:
            term = self.request.GET.get('term', self.request.GET['search'])
            for field in self.search_filters:
                query_filter = field + '__icontains'
                filtered_q |= q.model.objects.filter(**{query_filter: term})
            q = q & filtered_q
        if 'term' in self.request.GET:
            self.pagination_class = None
            q = q[0:20]
        return q


class OnlyDoctorRecords(object):

    def get_queryset(self):
        return super(OnlyDoctorRecords, self).get_queryset().filter(doctor=self.request.user.doctor)
