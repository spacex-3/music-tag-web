import django_filters


class TaskFilters(django_filters.FilterSet):
    state = django_filters.CharFilter(method='filter_state')

    def filter_state(self, queryset, name, value):
        if value in ['fail', 'failed']:
            return queryset.filter(state__in=['fail', 'failed'])
        return queryset.filter(state__iexact=value)
