import codecs
import logging
from typing import Iterable

import sqlparse
import importlib.util
from six import string_types
from collections import OrderedDict
from django.db import transaction, connection as connection_default

__all__ = ['get_sql_from_queryset', 'dict_fetchall', 'load_sql_from_file', 'load_sql_from_python_module']

logger = logging.getLogger(__name__)


def get_sql_from_queryset(qs):
    return sqlparse.format(
        connection_default.cursor().mogrify(*qs.query.sql_with_params()),
        reindent=True, indent_width=4
    )


def dict_fetchall(cursor, pk=None, pk_sep='-'):
    fields = [col[0] for col in cursor.description]
    if pk:
        if isinstance(pk, string_types):
            pk_index = '{%s}' % fields.index(pk)
        if type(pk) in [tuple, list, set]:
            pk_index = '{%s}' % '}}{0}{{'.format(pk_sep).join([str(fields.index(p)) for p in pk])
        return OrderedDict(
            (pk_index.format(*row), dict(zip(fields, row)))
            for row in cursor.fetchall()
        )
    else:
        return [
            dict(zip(fields, row))
            for row in cursor.fetchall()
        ]


def load_sql_from_file(filepath, connection=None):
    if not connection:
        connection = connection_default
    logger.info(f'Loading SQL from sql file "{filepath}"')
    sql = codecs.open(filepath, 'r', encoding='utf-8-sig').read()
    cursor = connection.cursor()
    try:
        cursor.execute(sql)
    except Exception as e:
        logger.warning(f'Couldn''t execute SQL from "{filepath}"', extra={'exception': e})
        transaction.rollback()
    else:
        transaction.commit()


def load_sql_from_python_module(filepath: str, connection=None):
    if not connection:
        connection = connection_default
    cursor = connection.cursor()
    try:
        module_spec = importlib.util.spec_from_file_location('sql', filepath)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        sql = getattr(module, 'SQL', None) or getattr(module, 'sql', None)
        logger.info(f'Loading SQL from python file "{filepath}"')
        if isinstance(sql, (list, set, tuple)):
            sql = '\n;\n'.join(sql)
        cursor.execute(sql)
        transaction.commit()
    except Exception as e:
        logger.warning(f'Couldn''t execute SQL from python file "{filepath}"', extra={'exception': e})
