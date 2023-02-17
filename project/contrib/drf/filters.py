from dateutil.relativedelta import relativedelta
from django.db.models import F, Q
from django.utils import timezone
from django_filters import MultipleChoiceFilter, ModelMultipleChoiceFilter
from django_filters.constants import EMPTY_VALUES
from django_filters.widgets import CSVWidget, DateRangeWidget as DateRangeWidgetBase
from django_filters.rest_framework import BooleanFilter, NumberFilter
from rest_framework.filters import OrderingFilter


class OrderingFilterNullsLast(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=True))
                else:
                    f_ordering.append(F(o).asc(nulls_last=True))

            return queryset.order_by(*f_ordering)

        return queryset


class OrderingFilterNullsFirst(OrderingFilter):
    def filter_queryset(self, request, queryset, view):
        ordering = self.get_ordering(request, queryset, view)

        if ordering:
            f_ordering = []
            for o in ordering:
                if not o:
                    continue
                if o[0] == '-':
                    f_ordering.append(F(o[1:]).desc(nulls_last=False))
                else:
                    f_ordering.append(F(o).asc(nulls_last=False))

            return queryset.order_by(*f_ordering)

        return queryset


class CSVWidgetFilterMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(widget=CSVWidget, *args, **kwargs)


class MultipleChoiceCommaSeparatedFilter(CSVWidgetFilterMixin, MultipleChoiceFilter):
    pass


class ModelMultipleChoiceCommaSeparatedFilter(CSVWidgetFilterMixin, ModelMultipleChoiceFilter):
    pass


class ModelMultipleChoiceCommaSeparatedIdFilter(CSVWidgetFilterMixin, ModelMultipleChoiceFilter):
    def filter(self, qs, value):
        if not value:
            return qs
        return super().filter(qs, [o.id if not isinstance(o, int) else o for o in value])


class DateRangeWidget(DateRangeWidgetBase):
    suffixes = ['from', 'to']


class IsNotValueFilter(BooleanFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return super().filter(qs, not value)


class IsNotEmptyFilter(BooleanFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        condition = Q(
            Q(**{f'{self.field_name}__isnull': True})
            | Q(**{f'{self.field_name}__exact': ''})
        )
        if value:
            condition = ~Q(condition)
        qs = self.get_method(qs)(condition)
        return qs


class IsNotNullFilter(BooleanFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        if self.distinct:
            qs = qs.distinct()
        condition = Q(**{f'{self.field_name}__isnull': True})
        if value:
            condition = ~Q(condition)
        qs = self.get_method(qs)(condition)
        return qs


class YearsFromDateFilter(NumberFilter):
    def filter(self, qs, value):
        if value in EMPTY_VALUES:
            return qs
        return super().filter(qs, timezone.now().date() - relativedelta(years=value))
