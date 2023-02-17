from project.settings.bits import redis as redis_settings

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'acc.User'

SESSION_COOKIE_NAME = '_id_'
CSRF_COOKIE_NAME = '_sec_'

SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_AGE = 3600 * 24 * 30
SESSION_COOKIE_ANONYMOUS_AGE = 3600 * 24 * 3

SESSION_ENGINE = 'redis_sessions.session'
SESSION_REDIS = {
    'host': redis_settings.REDIS_HOST,
    'port': redis_settings.REDIS_PORT,
    'db': redis_settings.REDIS_DB_SESSION,
    'retry_on_timeout': True,
    'socket_timeout': 2,
}
