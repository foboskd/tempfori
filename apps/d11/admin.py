import datetime
from typing import Optional

from django.contrib import admin
from django.db import models, transaction
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django_json_widget.widgets import JSONEditorWidget
from django_admin_listfilter_dropdown.filters import RelatedDropdownFilter, DropdownFilter
from rangefilter.filters import DateRangeFilter

from project.contrib.admin_tools.filter import IsNullFilter
from project.contrib.admin_tools.widget import JSONViewWidget
from d11 import models as d11_models
from d11.tasks import d11_mviews_rebuild
from d11.services.report_xlsx import get_doc_fields_report_xlsx


@admin.register(d11_models.Source)
class SourceAdmin(admin.ModelAdmin):
    list_display = ['label', 'collector_class']
    search_fields = ['label']
    formfield_overrides = {
        models.JSONField: {'widget': JSONEditorWidget},
    }


@admin.register(d11_models.DocField)
class FieldAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'label', 'label_aliases', 'type', 'is_auto', 'sorting']
    # list_editable = ['name', 'label', 'type', 'is_auto', 'sorting']
    list_filter = ['is_auto']
    search_fields = ['name', 'label']


class DocFieldValueInline(admin.TabularInline):
    template = 'admin/doc/fields_values_tabular_inline.html'
    model = d11_models.DocFieldValue
    readonly_fields = ['field', 'value', 'updated_at']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


class DocFileValueInline(admin.TabularInline):
    model = d11_models.DocFileValue
    fields = ['field', 'value', 'updated_at']
    readonly_fields = ['updated_at']
    extra = 0


class DocAlephCardInline(admin.StackedInline):
    template = 'admin/doc/aleph_cards_stacked_inline.html'

    model = d11_models.DocAlephCard
    formfield_overrides = {
        models.JSONField: {'widget': JSONViewWidget},
    }
    readonly_fields = ['kind', 'aleph_id', 'updated_at', 'aleph_fields_json']
    fields = ['kind', 'aleph_id', 'file', 'updated_at', 'aleph_fields_json']
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(d11_models.Doc)
class DocAdmin(admin.ModelAdmin):
    change_form_template = 'admin/doc/change_form.html'

    class FieldsUpdatedAtFilter(DateRangeFilter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title = _('Дата обновления на ВАК')

    class DefenseDateFilter(DateRangeFilter):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.title = _('Дата защиты')

    class FullNameDoublesIsNullFilter(IsNullFilter):
        parameter_name = lookup_field = 'full_name_doubles'
        title = _('Дубли ФИО')

    class AlephCardSynopsisIsNullFilter(IsNullFilter):
        parameter_name = 'aleph_synopsis'
        lookup_field = 'advanced_attributes__aleph_card_synopsis_id'
        title = _('Карточка автореферата')

    class AlephCardDissertationIsNullFilter(IsNullFilter):
        parameter_name = 'aleph_dissertation'
        lookup_field = 'advanced_attributes__aleph_card_dissertation_aleph_id'
        title = _('Карточка диссертации')

    inlines = [
        DocFileValueInline,
        DocFieldValueInline,
        DocAlephCardInline,
    ]
    list_filter = [
        ('source', RelatedDropdownFilter),
        ('is_checked', DropdownFilter),
        ('is_sync_synopsis_to_abis', DropdownFilter),
        ('is_sync_dissertation_to_abis', DropdownFilter),
        ('is_track_external', DropdownFilter),
        AlephCardSynopsisIsNullFilter,
        AlephCardDissertationIsNullFilter,
        # ('is_synopsis_exists', DropdownFilter),
        ('advanced_attributes__is_has_updates_after_abis_manual_changes', DropdownFilter),
        ('advanced_attributes__defense_date', DefenseDateFilter),
        ('advanced_attributes__values_updated_at_max', FieldsUpdatedAtFilter),
        FullNameDoublesIsNullFilter,
    ]
    list_display = [
        'id', '_full_name', '_defense_date', '_fields_updated_at', 'url', '_aleph_cards', 'is_checked',
        # 'is_synopsis_exists',
        'is_sync_synopsis_to_abis', 'is_sync_dissertation_to_abis', 'is_track_external',
        '_is_has_updates_after_abis_manual_changes',
    ]
    readonly_fields = ['source', ]
    save_on_top = True
    search_fields = ['url', 'fields_values__value']
    ordering = ['-id']
    exclude = ['content_file', 'content_file_hash', 'created_at', 'updated_at', 'url', ]
    actions = [
        'download_fields_xlsx'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            *self.model.objects.get_queryset_prefetch_related()
        )

    @admin.display(description=_('дата обновления на ВАК'), ordering='advanced_attributes__values_updated_at_max')
    def _fields_updated_at(self, instance: d11_models.Doc) -> datetime.datetime:
        return instance.advanced_attributes.values_updated_at_max

    @admin.display(description=_('защита'), ordering='advanced_attributes__defense_date')
    def _defense_date(self, instance: d11_models.Doc) -> Optional[datetime.date]:
        return instance.advanced_attributes.defense_date

    @admin.display(description=_('карточки'))
    def _aleph_cards(self, instance: d11_models.Doc) -> int:
        return len(instance.aleph_cards.all())

    @admin.display(description=_('фио'), ordering='advanced_attributes__full_name')
    def _full_name(self, instance: d11_models.Doc) -> str:
        return instance.advanced_attributes.full_name

    @admin.display(
        description=_(mark_safe('<div title="обновлено после внесения изменений в Алеф">обновлено после</div>')),
        ordering='advanced_attributes__is_has_updates_after_abis_manual_changes',
        boolean=True,
    )
    def _is_has_updates_after_abis_manual_changes(self, instance: d11_models.Doc) -> bool:
        return instance.advanced_attributes.is_has_updates_after_abis_manual_changes

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    @transaction.atomic
    def save_form(self, request, form, change):
        ret = super().save_form(request, form, change)
        transaction.on_commit(d11_mviews_rebuild.delay)
        return ret

    @admin.action(description=_('Скачать данные записей в .xlsx'))
    def download_fields_xlsx(self, request, queryset):
        wb = get_doc_fields_report_xlsx(queryset)
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=d11-{datetime.datetime.now().strftime("%Y%m%d")}.xlsx'
        wb.save(response)
        return response


@admin.register(d11_models.DocAlephCard)
class DocAlephCardAdmin(admin.ModelAdmin):
    search_fields = ['aleph_id', *[f'doc__{f}' for f in DocAdmin.search_fields]]
    list_display = ['aleph_id', 'kind', 'doc']
    list_filter = ['kind']
    formfield_overrides = {
        models.JSONField: {'widget': JSONViewWidget},
    }


@admin.register(d11_models.ImportFromAleph)
class ImportAlephAdmin(admin.ModelAdmin):
    list_display = ['id', 'docs_count', 'created_at', 'updated_at']
    readonly_fields = [
        'created_at', 'updated_at', 'docs_count', 'docs', 'result_file', 'extra'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('docs')


@admin.register(d11_models.ExportToAleph)
class ExportAlephAdmin(ImportAlephAdmin):
    list_display = ['id', 'kind', 'docs_count', 'created_at', 'updated_at']
    list_filter = ['kind']
    readonly_fields = ImportAlephAdmin.readonly_fields + ['docs_serialized_file', 'kind']


@admin.register(d11_models.CollectorImport)
class CollectorImportAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'collector_name',
        'docs_affected_count',
        'docs_total_count',
        'docs_created_count',
        'docs_updated_count',
        'created_at', 'updated_at'
    ]
    readonly_fields = ['docs_affected_count', 'docs_total_count', 'docs_created_count', 'docs_updated_count']
    exclude = ['docs']
    formfield_overrides = {
        models.JSONField: {'widget': JSONViewWidget},
    }

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('docs')


@admin.register(d11_models.DocAlephCardFilesExport)
class DocAlephCardFilesExportAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_all', 'docs_count', 'cards_count', 'created_at', 'updated_at']
    readonly_fields = [
        'is_all', 'created_at', 'updated_at', 'docs_count', 'cards_count', 'cards'
    ]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('cards', 'cards__doc')


@admin.register(d11_models.Ref)
class RefAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'from_what', 'to_what']
    list_filter = ['type']
