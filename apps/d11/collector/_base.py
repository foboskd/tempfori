import datetime
import pickle
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING, Dict, Union, Any, Type

from django.conf import settings
from django.utils.functional import classproperty

from d11.serializers.aleph import DocAlephSerializerAbstract
from d11.models.doc import DocFieldType
from d11.models.collector import CollectorImport

if TYPE_CHECKING:
    from d11.models.source import Source

__all__ = [
    'CollectorItemFieldValue',
    'CollectorItem',
    'CollectorItemList',
    'CollectorAbstract',
]


@dataclass
class CollectorItemFieldValue:
    label: str
    value: Union[str, int, float, datetime.date, datetime.datetime, Path]
    type: Optional[DocFieldType] = None

    def __post_init__(self):
        if not self.type:
            self.type = DocFieldType.STR


@dataclass
class CollectorItem:
    url: str
    fields_values: List[CollectorItemFieldValue]
    autoref_file_path: Optional[Path] = None
    disser_file_path: Optional[Path] = None


@dataclass
class CollectorItemList:
    items: List[CollectorItem]


class CollectorAbstract:
    source: 'Source'
    kwargs: Dict
    doc_serializer_aleph_class: Optional[Type[DocAlephSerializerAbstract]] = None
    _verbose_name: Optional[str] = None
    _import_instance: Optional[CollectorImport] = None

    def __init__(self, source: 'Source', **kwargs):
        self.source = source
        self.kwargs = kwargs

    @classproperty
    def verbose_name(cls):
        return cls._verbose_name or cls.__class__.__name__

    def get_or_create_import_instance(self) -> CollectorImport:
        if not self._import_instance:
            self._import_instance = CollectorImport(collector_name=self.__class__.__name__)
        return self._import_instance

    @abstractmethod
    def start(self, **kwargs) -> None:
        ...

    @abstractmethod
    def do_item(self, url: str) -> None:
        ...

    @abstractmethod
    def get_total_count(self, **kwargs) -> int:
        ...

    @classmethod
    def _cache_path_by_key(cls, key: str) -> Path:
        return Path(f'{settings.MEDIA_ROOT}'
                    f'/_collector_cache'
                    f'/{key[:2]}'
                    f'/{key[2:4]}'
                    f'/{key}.pickle')

    @classmethod
    def _cache_get(cls, key: str) -> Optional[Any]:
        cache_path = cls._cache_path_by_key(key)
        if settings.COLLECTOR_CACHE_ENABLED and cache_path.exists():
            with open(cache_path, 'rb') as cache:
                return pickle.load(cache)

    @classmethod
    def _cache_set(cls, key, data) -> bool:
        if not settings.COLLECTOR_CACHE_ENABLED:
            return False
        cache_path = cls._cache_path_by_key(key)
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_path, 'wb') as cache:
            pickle.dump(data, cache)
            return True
