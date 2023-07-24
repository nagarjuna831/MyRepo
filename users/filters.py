from django_filters import FilterSet
from django_filters import rest_framework as filters
from .models import User


class UserFilter(FilterSet):
    name = filters.CharFilter('name')
    email = filters.CharFilter('email')
    phone = filters.CharFilter('phone')
    is_superuser = filters.CharFilter('is_superuser')

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'is_superuser')
