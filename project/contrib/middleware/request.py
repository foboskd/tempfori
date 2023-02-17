from __future__ import absolute_import, division, print_function

import socket
import uuid
from contextvars import ContextVar
from typing import Optional

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils.log import log_response

_HTTP_REQUEST_VAR: ContextVar[HttpRequest] = ContextVar('http_request')
_HTTP_REQUEST_BODY_VAR: ContextVar[bytes] = ContextVar('http_request_body')


def build_absolute_uri(url: str) -> str:
    if request := get_request():
        return request.build_absolute_uri(url)
    return f'https://{settings.DOMAIN_NAME}%s' % (
            ('/' if not url.startswith('/') else '') + url
    )


def get_request() -> Optional[HttpRequest]:
    try:
        req: HttpRequest = _HTTP_REQUEST_VAR.get()
    except LookupError:
        return
    return req


def get_request_body() -> Optional[bytes]:
    try:
        body: bytes = _HTTP_REQUEST_BODY_VAR.get()
    except LookupError:
        return
    return body


def get_current_user(request: Optional[HttpRequest] = None):
    if not request:
        request = get_request()
    if request:
        return getattr(request, 'user', None)


def get_current_user_agent(request: Optional[HttpRequest] = None) -> str:
    if not request:
        request = get_request()
    if request:
        return getattr(request, 'META', {}).get('HTTP_USER_AGENT', '')


def get_current_user_ip(request: Optional[HttpRequest] = None) -> Optional[str]:
    ip = None
    if not request:
        request = get_request()
    if request:
        for what in ['HTTP_X_REAL_IP', 'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']:
            try:
                ip = list(map(lambda x: x.strip(), request.META.get(what).split(',')))[-1]
                socket.inet_aton(ip)
                break
            except BaseException:
                pass
    if not ip or ip.startswith('unix'):
        ip = '127.0.0.2'
    return ip


def get_current_user_domain(request: Optional[HttpRequest] = None):
    if not request:
        request = get_request()
    if not request:
        return settings.SITE_BASE_DOMAIN
    return request.META['HTTP_HOST']


def generate_request_id() -> str:
    return uuid.uuid4().hex


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request: HttpRequest) -> None:
        request.request_id = request.META.get('HTTP_X_REQUEST_ID', '') or generate_request_id()
        _HTTP_REQUEST_VAR.set(request)
        _HTTP_REQUEST_BODY_VAR.set(request.body)

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        if request_id := getattr(request, 'request_id', None):
            response['X-REQUEST-ID'] = request_id
        response['X-BACKEND'] = getattr(settings, 'BACKEND_ID', 0)
        log_response(
            '%s %s: %s', response.status_code, response.reason_phrase, request.path,
            response=response,
            request=request,
        )
        return response
