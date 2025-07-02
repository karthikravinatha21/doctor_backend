from rest_framework import filters
from django_filters import rest_framework as django_filters
from user_details.models import User


class UserFilter(django_filters.FilterSet):
    # Filtering by department, sub_department, and production_house
    department = django_filters.CharFilter(field_name='department__name', lookup_expr='icontains')
    sub_department = django_filters.CharFilter(field_name='sub_department__name', lookup_expr='icontains')
    production_house = django_filters.CharFilter(field_name='production_house__name', lookup_expr='icontains')

    # Filtering by email and mobile
    email = django_filters.CharFilter(field_name='email', lookup_expr='icontains')
    mobile = django_filters.CharFilter(field_name='mobile', lookup_expr='icontains')

    class Meta:
        model = User
        fields = ['department', 'sub_department', 'production_house', 'email', 'mobile']
