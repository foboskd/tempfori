from django.urls import reverse, NoReverseMatch
from drf_yasg import openapi
from drf_yasg.inspectors import RelatedFieldInspector, ChoiceFieldInspector as ChoiceFieldInspectorBase, NotHandled
from rest_framework.relations import PrimaryKeyRelatedField


class PrimaryKeyRelatedFieldInspector(RelatedFieldInspector):
    def field_to_swagger_object(self, field, swagger_object_type, use_references, **kwargs):
        if isinstance(field, PrimaryKeyRelatedField) and swagger_object_type == openapi.Schema:
            return super().field_to_swagger_object(field, swagger_object_type, use_references, **kwargs)
        return NotHandled

    def add_manual_fields(self, serializer_or_field, schema):
        if not serializer_or_field.queryset:
            return
        viewset_base_name = getattr(serializer_or_field, 'view_name', None)
        if not viewset_base_name:
            viewset_base_name = f'{serializer_or_field.queryset.model._meta.object_name.lower()}'
        for suffix, view_args in [
            ['list', []],
            ['detail', ['$id']],
        ]:
            try:
                setattr(schema, f'x-url-object-{suffix}', reverse(viewset_base_name + '-' + suffix, args=view_args))
            except NoReverseMatch:
                pass


class ChoiceFieldInspector(ChoiceFieldInspectorBase):
    def add_manual_fields(self, serializer_or_field, schema):
        if serializer_or_field.choices:
            setattr(schema, 'x-enum-description', serializer_or_field.choices)
