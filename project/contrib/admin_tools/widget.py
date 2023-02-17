import json

from django.forms import Widget
from django.utils.safestring import mark_safe
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.data import JsonLexer


class JSONViewWidget(Widget):
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            return None
        return mark_safe(highlight(
            json.dumps(json.loads(value), indent=4, ensure_ascii=False),
            JsonLexer(),
            HtmlFormatter(linenos=True)
        ))
