from project.settings.bits import redis as redis_settings
from project.settings import TIME_ZONE

CELERY = {
    'broker_url': 'redis://%s:%s/%s' % (
        redis_settings.REDIS_HOST,
        redis_settings.REDIS_PORT,
        redis_settings.REDIS_DB_CELERY
    ),
    'enable_utc': True,
    'timezone': TIME_ZONE,
    'accept_content': ['json', 'pickle'],
    'task_serializer': 'pickle',
    'result_serializer': 'pickle',
    'worker_disable_rate_limits': True,
    'worker_pool_restarts': True,
    'task_ignore_result': True,
    'result_expires': 60 * 60 * 4,
    'beat_scheduler': 'django_celery_beat.schedulers.DatabaseScheduler',
}
