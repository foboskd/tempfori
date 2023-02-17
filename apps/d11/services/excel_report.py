import pprint

from openpyxl import Workbook
from django.conf import settings
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE

from d11.models import Doc, DocAlephCardKind


def create_excel_report(docs_queryset: Doc.QuerySet) -> Workbook:
    wb = Workbook()
    sh = wb.active
    sh.append([
        'D11 ID',
        'ФИО',
        'Дата первичной публикации объявления',
        'Дата защиты диссертации',
        'Тип диссертации',
        'Отрасль науки',
        'Шифр научной специальности',
        'Тема диссертации',
        'Шифр диссертационного совета',
        'Наименование организации место защиты',
        'URL',
        'Автореферат / Aleph ID',
        'Автореферат / Файл / URL D11',
        'Автореферат / Файл / URL Источник',
        'Диссертация / Aleph ID',
        'Диссертация / Файл / URL D11',
        'Диссертация / Файл / URL Источник',
    ])

    for doc in docs_queryset:
        doc: Doc
        cards = doc.get_cards_dict()
        row = [
            doc.id,
            doc.get_value_by_name('full_name'),
            doc.get_value_by_name('publication_date'),
            doc.get_value_by_name('defense_date'),
            doc.get_value_by_name('kind'),
            doc.get_value_by_name('industry'),
            doc.get_value_by_name('specialty_code'),
            doc.get_value_by_name('subject'),
            doc.get_value_by_name('council_code'),
            doc.get_value_by_name('place_name'),
            doc.url,
        ]
        for card_kind in [
            DocAlephCardKind.SYNOPSIS,
            DocAlephCardKind.DISSERTATION,
        ]:
            card = cards[card_kind]
            file_source_field_name = 'autoref_external_source_url'
            if card_kind == DocAlephCardKind.DISSERTATION:
                file_source_field_name = 'disser_external_source_url'
            row += [
                card.aleph_id,
                f'{settings.BASE_URL}{card.file.url}' if card.file else None,
                ILLEGAL_CHARACTERS_RE.sub(r'', (doc.get_value_by_name(file_source_field_name) or '').replace('\n', '')),
            ]
        sh.append(row)
    return wb
