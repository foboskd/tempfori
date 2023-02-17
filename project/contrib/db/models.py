from typing import List
import time
import logging
from django.apps import apps as django_apps
from django.db import models, transaction, connection as connection_default, NotSupportedError
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class DatesModelBase(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name=_('создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('обновлено'))


class ModelDiffMixin:
    __initial__ = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__initial__ = self._dict

    @property
    def diff(self):
        d1 = self.__initial__
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.__initial__ = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in self._meta.fields])


class MaterializedViewModel(models.Model):
    rebuild_dependency: List[str] = []

    class Manager(models.Manager):
        def get_rebuild_names(self):
            return [self.model._meta.db_table] + self.model.rebuild_dependency

        @transaction.atomic
        def rebuild(self, connection=None, is_not_concurrently=False, attempt=0):
            t = time.time()
            if not connection:
                connection = connection_default
            names = self.get_rebuild_names()
            logger_msg = f'Rebuild DB MViews {names}'
            logger.info(f'START – {logger_msg}')
            self._pre_rebuild(names, connection)
            sql = ';\n'.join(map(
                lambda x: 'REFRESH MATERIALIZED VIEW %s %s' % ('CONCURRENTLY' if not is_not_concurrently else '', x),
                names
            ))
            sid = transaction.savepoint()
            try:
                connection.cursor().execute(sql)
                transaction.savepoint_commit(sid)
            except NotSupportedError as e:
                transaction.savepoint_rollback(sid)
                if attempt > 1:
                    raise e
                logger.warning(str(e), extra={'data': {'error': e.args}})
                self.rebuild(connection=connection, is_not_concurrently=True, attempt=attempt + 1)
            self._post_rebuild(names, connection)
            logger.info(f'OK – {logger_msg}')
            return time.time() - t

        def _pre_rebuild(self, names, connection):
            ...

        def _post_rebuild(self, names, connection):
            from cacheops import invalidate_model
            for model in django_apps.get_models():
                if model._meta.db_table in names:
                    invalidate_model(model)

    class Meta:
        abstract = True
        
    objects = Manager()

    def save(self, *args, **kwargs):
        return

    def delete(self, *args, **kwargs):
        return
