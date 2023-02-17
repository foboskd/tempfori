from project.settings.bits import redis as redis_settings

CACHES = {
    cache_name: {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{redis_settings.REDIS_HOST}:{redis_settings.REDIS_PORT}/{cache_db}',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'DB': cache_db
        }
    }
    for cache_name, cache_db in [
        ['default', redis_settings.REDIS_DB_CACHE_DEFAULT],
        ['select2', redis_settings.REDIS_DB_CACHE_SELECT2],
    ]
}

CACHEOPS_ENABLED = True

CACHEOPS_REDIS = {
    'host': redis_settings.REDIS_HOST,
    'port': redis_settings.REDIS_PORT,
    'db': redis_settings.REDIS_DB_CACHE_CACHEOPS,
}
CACHEOPS_DEFAULTS = {
    'timeout': 60 ** 2 * 24 * 365
}
CACHEOPS = {
    'auth.*': {'ops': 'all'},
    'acc.*': {'ops': 'all'},
    'd11.*': {'ops': 'all'},
    'sorl.thumbnail.*': {'ops': 'all'},
}

COLLECTOR_CACHE_ENABLED = False
