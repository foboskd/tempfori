import enum
from typing import Optional, Dict

from django.db import models
from rest_framework import fields
from rest_framework.relations import PrimaryKeyRelatedField


class EnumField(fields.ChoiceField):
    def __init__(
            self,
            choices=None,
            default=None,
            to_choice=lambda x: (x.value, x.name),
            to_repr=lambda x: x.name,
            **kwargs
    ):
        self.enum_class = choices
        self.to_repr = to_repr
        self.to_choice = to_choice
        kwargs['choices'] = [to_choice(e) for e in self.enum_class]
        if isinstance(default, enum.Enum):
            default = default.value
        kwargs['default'] = default
        kwargs.pop('max_length', None)
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        try:
            return self.enum_class(data)
        except (KeyError, ValueError):
            pass
        self.fail('invalid_choice', input=data)

    def to_representation(self, value):
        if not value:
            return None
        if isinstance(value, enum.Enum):
            return self.to_repr(value)
        else:
            return value


class CurrentUserIdDefault(fields.CurrentUserDefault):
    def __call__(self, serializer_field):
        return serializer_field.context['request'].user.id


class PrimaryKeyRelatedIdField(PrimaryKeyRelatedField):
    view_name: str = Optional[str]
    kwargs: Dict

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.view_name = kwargs.pop('view_name', None)
        super().__init__(**kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        if 'request' in self.context and hasattr(queryset, 'filter_by_user'):
            return queryset.filter_by_user(self.context['request'].user)
        return queryset

    def bind(self, field_name, parent):
        if self.label is None and self.queryset:
            self.label = self.get_default_label()
        super().bind(field_name, parent)

    def get_default_label(self) -> str:
        return self.queryset.model._meta.verbose_name.replace('_', ' ').capitalize()

    def get_default(self):
        default = super().get_default()
        if default and isinstance(default, models.Model):
            return default.id
        return default

    def to_internal_value(self, data):
        value = super().to_internal_value(data)
        try:
            return value.id
        except Exception:
            return int(data)

    def to_representation(self, value):
        if isinstance(value, int):
            return value
        return super().to_representation(value)
