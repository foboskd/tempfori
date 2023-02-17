from django_filters.rest_framework import DjangoFilterBackend


class FilterBackend(DjangoFilterBackend):
    def get_schema_fields(self, view):
        return super().get_schema_fields(view)
