from drf_yasg.app_settings import SWAGGER_DEFAULTS

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'project.contrib.drf.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'project.contrib.drf.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'project.contrib.drf.backends.FilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'project.contrib.drf.pagination.DefaultPagination',
    'DEFAULT_RENDERER_CLASSES': (
        'drf_ujson.renderers.UJSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'drf_ujson.parsers.UJSONParser',
    ),
    'EXCEPTION_HANDLER': 'project.contrib.drf.exceptions.custom_exception_handler',
}

SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': [],
    'USE_SESSION_AUTH': True,
    'REFETCH_SCHEMA_WITH_AUTH': True,
    'DISPLAY_OPERATION_ID': False,
    'DEFAULT_PAGINATOR_INSPECTORS': [
        'project.contrib.drf.schema.inspectors.query.DefaultPaginationRestResponsePagination',
        *SWAGGER_DEFAULTS['DEFAULT_PAGINATOR_INSPECTORS'],
    ],
    'DEFAULT_FIELD_INSPECTORS': [
        'project.contrib.drf.schema.inspectors.field.PrimaryKeyRelatedFieldInspector',
        'project.contrib.drf.schema.inspectors.field.ChoiceFieldInspector',
        *[
            f
            for f in SWAGGER_DEFAULTS['DEFAULT_FIELD_INSPECTORS']
            if f not in [
                'drf_yasg.inspectors.ChoiceFieldInspector',
            ]
        ],
    ]
}
