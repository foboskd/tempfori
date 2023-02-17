from django import forms
from django.contrib.admin import SimpleListFilter
from django_select2.forms import ModelSelect2Widget


class ModelAutocompleteFilter(SimpleListFilter):
    model_queryset = None
    lookup_field = NotImplemented
    model_search_fields = NotImplemented
    template = 'admin_tools/model-autocomplete-filter.html'

    def __init__(self, request, *args, **kwargs):
        self.request = request
        super().__init__(request, *args, **kwargs)

    def queryset(self, request, queryset):
        try:
            return queryset.filter(**{self.lookup_field: int(self.value())})
        except Exception:
            return queryset

    @property
    def field(self):
        filter_instance = self
        selected_value = self.request.GET.get(self.parameter_name)

        class Form(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields[filter_instance.parameter_name] = forms.ModelChoiceField(
                    widget=ModelSelect2Widget(
                        search_fields=filter_instance.model_search_fields,
                        attrs={
                            'data-ajax--delay': 1200,
                            'data-minimum-input-length': 0,
                            'data-theme': 'admin-autocomplete',
                        }
                    ),
                    queryset=filter_instance.model_queryset,
                    required=False,
                    initial=selected_value,
                )

        return Form()[self.parameter_name]

    def lookups(self, request, model_admin):
        return [
            ['__%s__' % self.parameter_name, None]
        ]


class IsNullFilter(SimpleListFilter):
    lookup_field = NotImplemented

    def lookups(self, request, model_admin):
        return (
            (1, 'Yes',),
            (0, 'No',),
        )

    def queryset(self, request, queryset):
        try:
            return queryset.filter(**{f'{self.lookup_field}__isnull': not bool(int(self.value()))})
        except Exception:
            return queryset
