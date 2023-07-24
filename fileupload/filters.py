from django_filters import FilterSet
from django_filters import rest_framework as filters
from .models import Files

class FileFilter(FilterSet):
    id = filters.CharFilter('id')
    file = filters.CharFilter('file')
    date_added = filters.CharFilter('date_added')
    user = filters.CharFilter('user')

    class Meta:
        model = Files
        fields = ('id', 'date_added', 'file', 'user','name','type')