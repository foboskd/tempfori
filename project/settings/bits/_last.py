import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from project.settings import BASE_DIR, SENTRY_DSN

PROJECT_TITLE = 'D11'
PROJECT_ADMIN_TITLE = f'{PROJECT_TITLE} – менеджерская панель'
PROJECT_API_TITLE = f'{PROJECT_TITLE} API'

PROJECT_APPS = [
    'acc',
    'main',
    'd11',
]

ADVANCED_APPS = [
    'project.contrib.management',
    'project.contrib.admin_tools',
    'project.contrib.db',
    'project.contrib.drf',
]

INSTALLED_APPS = (
        [
            'django.contrib.admin',
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'django.contrib.staticfiles',
            'django.contrib.humanize',
            'django_select2',
            'django_extensions',
            'django_json_widget',
            'django_pickling',
            'djcelery_email',
            'django_celery_beat',
            'django_filters',
            'cacheops',
            'rangefilter',
            'webshell',
            'django_admin_listfilter_dropdown',
            'admin_auto_filters',
            'drf_yasg',
            'django_rest_passwordreset',
        ]
        + ADVANCED_APPS
        + PROJECT_APPS
)

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates',
        ],
        'OPTIONS': {
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'project.contrib.template.context_processors.settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

FIXTURE_DIRS = [
    BASE_DIR / 'fixtures'
]

if DEBUG:
    MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS.append('debug_toolbar')
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda _request: True
    }

SILENCED_SYSTEM_CHECKS = [
    'debug_toolbar.W006',
]

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        send_default_pii=True,
    )
