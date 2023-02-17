import itertools

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.filters import SearchFilter
from django_filters import FilterSet, BooleanFilter, DateFilter, DateTimeFilter
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from project.contrib.drf.openapi import openapi_manual_parameter_bool, openapi_manual_parameter_array
from project.contrib.drf.permissions import IsSuperUser
from project.contrib.drf.filters import (
    OrderingFilterNullsLast, ModelMultipleChoiceCommaSeparatedFilter, IsNotNullFilter
)
from project.contrib.drf.backends import FilterBackend
from d11 import models as d11_models
from d11.api import serializers as d11_serializers


class SourceViewSet(ReadOnlyModelViewSet):
    queryset = d11_models.Source.objects.all()
    serializer_class = d11_serializers.SourceSerializer


class RefViewSet(ReadOnlyModelViewSet):
    queryset = d11_models.Ref.objects.all()
    serializer_class = d11_serializers.RefSerializer


class DocFieldViewSet(ReadOnlyModelViewSet):
    queryset = d11_models.DocField.objects.all()
    serializer_class = d11_serializers.DocFieldSerializer
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'sorting', 'name', 'label']
    ]))
    ordering = ['sorting', 'name', 'label']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=ordering_fields), default=ordering,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class DocViewSet(ModelViewSet):
    class Filter(FilterSet):
        source_id = ModelMultipleChoiceCommaSeparatedFilter(queryset=d11_models.Source.objects)
        is_aleph_card_synopsis_exists = IsNotNullFilter(field_name='advanced_attributes__aleph_card_synopsis_id')
        is_aleph_card_dissertation_exists = IsNotNullFilter(
            field_name='advanced_attributes__aleph_card_dissertation_aleph_id')
        is_has_updates_after_abis_manual_changes = BooleanFilter(
            field_name='advanced_attributes__is_has_updates_after_abis_manual_changes')
        is_full_name_duplicates = IsNotNullFilter(field_name='full_name_doubles')
        defense_date_lte = DateFilter(field_name='advanced_attributes__defense_date', lookup_expr='lte')
        defense_date_gte = DateFilter(field_name='advanced_attributes__defense_date', lookup_expr='gte')
        values_updated_at_max_lte = DateTimeFilter(
            field_name='advanced_attributes__values_updated_at_max', lookup_expr='lte')
        values_updated_at_max_gte = DateTimeFilter(
            field_name='advanced_attributes__values_updated_at_max', lookup_expr='gte')

        class Meta:
            model = d11_models.Doc
            fields = [
                'is_checked', 'is_sync_synopsis_to_abis', 'is_sync_dissertation_to_abis', 'is_track_external',
            ]

    http_method_names = ['get', 'patch']
    queryset = d11_models.Doc.objects
    permission_classes = [IsSuperUser]
    serializer_class = d11_serializers.DocSerializer
    serializer_read_class = d11_serializers.DocReadSerializer
    filter_backends = [FilterBackend, OrderingFilterNullsLast, SearchFilter]
    filterset_class = Filter
    search_fields = ['url', 'fields_values__value']
    ordering_fields = list(itertools.chain(*[
        [k, f'-{k}']
        for k in ['id', 'created_at', 'updated_at', ]
    ]))
    ordering = ['-updated_at']

    def get_serializer_class(self):
        return {
            'list': d11_serializers.DocReadListSerializer,
            'retrieve': d11_serializers.DocReadSerializer,
        }.get(
            self.action,
            d11_serializers.DocSerializer
        )

    def get_queryset(self):
        return super().get_queryset().prefetch_related(
            *self.queryset.model.objects.get_queryset_prefetch_related()
        )

    @swagger_auto_schema(
        manual_parameters=[
            openapi_manual_parameter_array('source_id', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_checked', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_sync_synopsis_to_abis', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_sync_dissertation_to_abis', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_track_external', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_aleph_card_synopsis_exists', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_aleph_card_dissertation_exists', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_has_updates_after_abis_manual_changes', openapi.IN_QUERY),
            openapi_manual_parameter_bool('is_full_name_duplicates', openapi.IN_QUERY),
            openapi.Parameter(
                'defense_date_lte', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                required=False,
            ),
            openapi.Parameter(
                'defense_date_gte', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE,
                required=False,
            ),
            openapi.Parameter(
                'values_updated_at_max_lte', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                required=False,
            ),
            openapi.Parameter(
                'values_updated_at_max_gte', openapi.IN_QUERY, type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                required=False,
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING, enum=ordering_fields), default=ordering,
            ),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
