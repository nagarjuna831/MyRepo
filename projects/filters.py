from django_filters import FilterSet
from django_filters import rest_framework as filters
from .models import Project


class ProjectFilter(FilterSet):
    name = filters.CharFilter('name')
    description = filters.CharFilter('email')
    date_added = filters.CharFilter('phone')
    date_updated = filters.CharFilter('is_superuser')
    user = filters.CharFilter('user')

    class Meta:
        model = Project
        fields = ('name', 'description', 'date_added', 'date_updated','user')
