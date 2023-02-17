import pytz

from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin

__all__ = ['TimezoneMiddleware']


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tzname = request.session.get('timezone')
        if tzname:
            timezone.activate(pytz.timezone(tzname))
        else:
            timezone.deactivate()
