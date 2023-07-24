from django_filters import FilterSet
from django_filters import rest_framework as filters
from .models import Template, Fields,FormData


class TemplateFilter(FilterSet):
    label = filters.CharFilter('label')
    date_added = filters.CharFilter('date_added')
    date_updated = filters.CharFilter('date_updated')
    description = filters.CharFilter('description')

    class Meta:
        model = Template
        fields = ('label', 'date_added', 'date_updated', 'description')


class FieldsFilter(FilterSet):
    template = filters.CharFilter('template')
    label = filters.CharFilter('label')
    type = filters.CharFilter('type')
    date_added = filters.CharFilter('date_added')

    class Meta:
        model = Fields
        fields = ('template', 'label', 'type', 'date_added')


class FormDataFilter(FilterSet):
    template = filters.CharFilter('template')
    user = filters.CharFilter('user')
    
    class Meta:
        model = Fields
        fields = ('template', 'user')