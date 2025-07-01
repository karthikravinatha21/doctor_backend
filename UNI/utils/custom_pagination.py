import math
from collections import OrderedDict
from django.conf import settings
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    page_size_query_param = 'page_count'
    max_page_size = 100000

    def get_custom_page_number(self):
        if self.page:
            return self.page.number
        return None

    def get_paginated_response(self, data):
        return OrderedDict([
            ('total_count', self.page.paginator.count),
            ('current_page_number', self.get_custom_page_number()),
            ('next_page', self.get_next_link()),
            ('previous_page', self.get_previous_link()),
        ])


def query_based_pagination(self,queryset,request,list_all=False):
    
    if ('paginate' in request.query_params and request.query_params.get('paginate') in [False,'false','False'] or list_all):
        datalist = self.get_serializer(queryset, many=True).data
        response = {
            "data": datalist
        }
        
        return response
        
    page_size = request.query_params.get('page_count')  # Get page size from query param
    self.pagination_class.page_size = int(page_size) if page_size else 10  # Default to 10 if not provided
    
    page = self.paginate_queryset(queryset)
    
    if page is not None:
        serializer = self.get_serializer(page, many=True)
        pagination_data= self.get_paginated_response(serializer.data)
        
    datalist = serializer.data
    response = {
        "data": datalist,
        "pagination_data": pagination_data
    }
    
    return response



def custom_paginate(data_list, page=1, page_size=settings.PAGE_SIZE):
    total_count = len(data_list)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = data_list[start_index:end_index]
    total_pages = math.ceil(total_count / page_size)

    next_page = None
    next_page_number = None
    if end_index < total_count:
        next_page = f'?page={page + 1}'
        next_page_number = page + 1

    previous_page = None
    previous_page_number = None
    if start_index > 0:
        previous_page = f'?page={page - 1}'
        previous_page_number = page - 1

    paginated_response = {
        'data': paginated_data,
        'total_count': total_count,
        'next_page': next_page,
        'next_page_number': next_page_number,
        'previous_page': previous_page,
        'previous_page_number': previous_page_number,
        'total_pages': total_pages
    }

    return paginated_response
