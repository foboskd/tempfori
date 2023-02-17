from django.template import Library
from django.utils.safestring import mark_safe
from pygments.formatters.html import HtmlFormatter

register = Library()


@register.simple_tag()
def pygments_highlight_style():
    return mark_safe('<style>%s</style>' % HtmlFormatter().get_style_defs())
