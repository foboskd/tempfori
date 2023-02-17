import logging
from typing import Optional
import datetime
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from django.conf import settings

logger = logging.getLogger(__name__)


def _d(v: Optional[datetime.datetime]) -> datetime.datetime:
    return v.replace(tzinfo=None) if v else None


def _b(v: Optional[bool]) -> int:
    return int(v) or 0


def _f(v) -> str:
    if not v:
        return v
    return f'{settings.BASE_URL}{v.value.url}'


def get_doc_fields_report_xlsx(queryset) -> Workbook:
    wb = Workbook()
    ws = wb.active
    titles = [
        'ФИО',
        'Тип диссертации',
        'Тема диссертации',
        'URL',
        'Дата первичной публикации объявления',
        'Дата защиты диссертации',
        'Дата последнего сделанного в Алеф изменения',
        'Запись обновлена после внесения изменения в Алеф?',
        'Проверено?',
        'Загрузить автореферат в Алеф?',
        'Загрузить диссертацию в Алеф?',
        'Отслеживать ВАК?',
        'Дата создания в D11',
        'Дата последнего обновления в D11',
        'D11 ID',
        'Автореферат Aleph ID',
        'Автореферат Aleph дата создания',
        'Диссертация Aleph ID',
        'Диссертация Aleph дата создания',
        'Файл автореферата',
        'Файл диссертации',
        'Отрасль науки',
        'Шифр научной специальности',
        'Шифр диссертационного совета',
        'Наименование организации место защиты',
        'Адрес организации',
        'Телефон организации',
        'Интернет-адрес текста автореферата на сайте организации',
        'Интернет-адрес объявления на сайте организации',
        'Интернет-адрес текста диссертации на сайте организации',
    ]
    ws.append(titles)
    for doc in queryset.prefetch_related(
            *queryset.model.objects.get_queryset_prefetch_related()
    ):
        row = [
            doc.get_value_by_name('full_name'),  # ФИО
            doc.get_value_by_name('kind'),  # Тип диссертации
            doc.get_value_by_name('subject'),  # Тема диссертации
            doc.url,  # url
            doc.get_value_by_name('publication_date'),  # Дата первичной публикации объявления
            doc.get_value_by_name('defense_date'),  # Дата защиты диссертации
            _d(doc.last_date_abis_manual_changes),  # Дата последнего сделанного в Алеф изменения
            int(doc.advanced_attributes.is_has_updates_after_abis_manual_changes) or 0,  # Запись обновлена после …
            _b(doc.is_checked),  # Проверено
            _b(doc.is_sync_synopsis_to_abis),  # Загрузить автореферат в Алеф
            _b(doc.is_sync_dissertation_to_abis),  # загрузить диссертацию в Алеф
            _b(doc.is_track_external),  # Отслеживать ВАК?
            _d(doc.advanced_attributes.values_created_at_min),  # дата создания в D11
            _d(doc.advanced_attributes.values_updated_at_max),  # дата последнего обновления в D11
            doc.id,  # D11 ID
            doc.advanced_attributes.aleph_card_synopsis_aleph_id,  # Автореферат Aleph ID
            _d(doc.advanced_attributes.aleph_card_synopsis_aleph_created_at),  # Автореферат Aleph дата создания
            doc.advanced_attributes.aleph_card_dissertation_aleph_id,  # Диссертация Aleph ID
            _d(doc.advanced_attributes.aleph_card_dissertation_created_at),  # Диссертация Aleph дата создания
            _f(doc.get_file_value_by_name('autoref_file')),  # Файл автореферата
            _f(doc.get_file_value_by_name('disser_file')),  # Файл диссертации
            doc.get_value_by_name('industry'),  # Отрасль науки
            doc.get_value_by_name('specialty_code'),  # Шифр научной специальности
            doc.get_value_by_name('council_code'),  # Шифр диссертационного совета
            doc.get_value_by_name('place_name'),  # Наименование организации место защиты
            doc.get_value_by_name('address'),  # Адрес организации
            doc.get_value_by_name('phone'),  # Телефон организации
            doc.get_value_by_name('autoref_external_source_url'),  # Интернет-адрес текста автореферата на сайте …
            doc.get_value_by_name('external_source_url'),  # Интернет-адрес объявления на сайте организации
            doc.get_value_by_name('disser_external_source_url'),  # Интернет-адрес текста диссертации на сайте …
        ]
        for i, value in enumerate(row):
            if isinstance(value, str):
                row[i] = ILLEGAL_CHARACTERS_RE.sub('', value)
        try:
            ws.append(row)
        except Exception as e:
            logging.error('Docs report XLSX', extra={
                'doc_id': doc.id,
                'error_class': e.__class__.__name__,
                'error': str(e),
                'doc_row': row
            })
            raise e
    return wb
