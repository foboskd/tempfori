from collections import OrderedDict
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class DefaultPagination(PageNumberPagination):
    page_size = 100
    max_page_size = 1000
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('max_page_size', self.max_page_size),
            ('page_size', self.page.paginator.per_page),
            ('page_number', self.page.number),
            ('page_next', self.get_next_link()),
            ('page_previous', self.get_previous_link()),
            ('results', data)
        ]))
