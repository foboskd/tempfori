import logging

from django.core.mail import EmailMultiAlternatives as EmailMultiAlternativesBase
from django.conf import settings
from django.template import Context, Template

from .template import EMAIL_TEMPLATE

__all__ = ['get_email_message_by_template', 'EmailMultiAlternatives']

logger = logging.getLogger(__name__)


class EmailMultiAlternatives(EmailMultiAlternativesBase):
    def send(self, *args, **kwargs):
        try:
            return super().send(*args, **kwargs)
        except Exception as e:
            logger.exception(str(e))
            raise e


def get_email_message_by_template(template_name: str, **kwargs) -> EmailMultiAlternatives:
    context = kwargs
    context.update(settings.EMAIL_CONTEXT)
    tpl = EMAIL_TEMPLATE[template_name]
    subject = Template(tpl.subject).render(Context(context))
    context.update({'subject': subject})
    body_text = '''{%% extends 'email/layout.txt' %%}{%% block content %%}%s{%% endblock %%}''' % tpl.body_text
    body_text = Template(body_text).render(Context(context))
    body_html = '''{%% extends 'email/layout.html' %%}
{%% block email_title %%}%s{%% endblock %%}
{%% block email_text %%}%s{%% endblock %%}''' % (tpl.subject, tpl.body_html)
    body_html = Template(body_html).render(Context(context))
    msg = EmailMultiAlternatives()
    msg.email_template = tpl
    msg.subject = subject
    msg.body = body_text
    if body_html:
        msg.attach_alternative(body_html, 'text/html')
    return msg
