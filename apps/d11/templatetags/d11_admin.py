import json
from django import template
from django.conf import settings
from django.contrib.admin.helpers import AdminReadonlyField
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer
from urllib.parse import unquote

from d11.models import DocFieldValue

register = template.Library()


@register.simple_tag()
def d11_admin_doc_field_value(field: AdminReadonlyField):
    doc_field_value: DocFieldValue = field.form.instance
    ret = doc_field_value.python_value
    if doc_field_value.field.name:
        if 'url' in doc_field_value.field.name:
            ret = f'<a href="{doc_field_value.python_value}" target="_blank">{doc_field_value.python_value}</a>'
        elif 'file' in doc_field_value.field.name:
            file_url = str(doc_field_value.python_value).replace(str(settings.MEDIA_ROOT), settings.MEDIA_URL[:-1])
            file_title = str(doc_field_value.python_value).replace(str(settings.MEDIA_ROOT), '')[1:]
            ret = f'<a href="{file_url}" target="_blank">{file_title}</a>'
    return mark_safe(ret)


@register.filter(safe=True)
def d11_admin_jsonify(what):
    return mark_safe(highlight(
        json.dumps(what, indent=4, ensure_ascii=False),
        JsonLexer(),
        HtmlFormatter(linenos=True)
    ))
