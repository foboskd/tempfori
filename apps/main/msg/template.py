from collections import namedtuple

__all__ = ['EMAIL_TEMPLATE']

EmailTemplate = namedtuple('EmailTemplate', ['subject', 'body_text', 'body_html'])

EMAIL_TEMPLATE = {
    'test': EmailTemplate(
        'TEST TEST TEST',
        'TEST TEST TEST\nTEST TEST TEST',
        '<h1>TEST TEST TEST</h1><h2>TEST TEST TEST</h2><h3>TEST TEST TEST</h3>',
    ),
    'import-notification': EmailTemplate(
        'Обновления записей в АЛЕФе (D11)',
        '',
        ''
    ),
}
