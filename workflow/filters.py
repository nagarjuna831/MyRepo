from django_filters import FilterSet
from django_filters import rest_framework as filters
from .models import *


class WorkflowFilter(FilterSet):
    label = filters.CharFilter('label')
    date_added = filters.CharFilter('date_added')
    date_updated = filters.CharFilter('date_updated')
    description = filters.CharFilter('description')

    class Meta:
        model = Workflow
        fields = ('label', 'date_added', 'date_updated', 'description')


class StateFilter(FilterSet):
    workflow = filters.CharFilter('workflow')
    date_added = filters.CharFilter('date_added')
    date_updated = filters.CharFilter('date_updated')

    class Meta:
        model = State
        fields = ('date_added', 'date_updated', 'workflow')
