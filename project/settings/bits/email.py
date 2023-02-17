# all in project.settings.envs.…


import os
from . import *

EMAIL_HOST = os.getenv('EMAIL_HOST', 'owa.rsl.ru')
EMAIL_PORT = os.getenv('EMAIL_PORT', 25)
EMAIL_HOST_USER = os.getenv('EMAIL_USER', 'BaranovAA@rsl.ru')
EMAIL_USE_TLS = False

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'

CELERY_EMAIL_CHUNK_SIZE = 1
CELERY_EMAIL_TASK_CONFIG = {
    'name': 'djcelery_email_send',
    'rate_limit': '500/m',
    'ignore_result': True,
}

EMAIL_CONTEXT = {
    'BASE_URL': BASE_URL,
    'info_email': 'BaranovAA@rsl.ru',
}

NOTICE_EMAILS = [
    'danilchenkoly@rsl.ru',  # uyKNm2gV26DjJT8
    'baranovaa@rsl.ru',
    'lushnikovpy@rsl.ru',
    'SakirkoIL@rsl.ru',  # LahXdw3irbSaFnx
    'BulgakovaTV@rsl.ru',  # LkxBpwUFugqB4qV
    'PrasolovaSV@rsl.ru',  # bHpUA5296XMgRjM
]
