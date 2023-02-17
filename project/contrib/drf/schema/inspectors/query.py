from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.inspectors import DjangoRestResponsePagination

from project.contrib.drf.pagination import DefaultPagination


class DefaultPaginationRestResponsePagination(DjangoRestResponsePagination):
    def get_paginated_response(self, paginator, response_schema):
        assert response_schema.type == openapi.TYPE_ARRAY, "array return expected for paged response"
        paged_schema = None
        s = openapi.Schema
        if isinstance(paginator, DefaultPagination):
            paged_schema = openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties=OrderedDict((
                    ('total', s(type=openapi.TYPE_INTEGER)),
                    ('max_page_size', s(type=openapi.TYPE_INTEGER)),
                    ('page_size', s(type=openapi.TYPE_INTEGER)),
                    ('page_number', s(type=openapi.TYPE_INTEGER)),
                    ('page_next', s(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('page_previous', s(type=openapi.TYPE_STRING, format=openapi.FORMAT_URI, x_nullable=True)),
                    ('results', response_schema),
                )),
                required=['total', 'max_page_size', 'page_size', 'page_number', 'results']
            )
        return paged_schema
