import socket
from pathlib import Path
from typing import Optional

from smb.SMBConnection import SMBConnection
from django.db import transaction
from django.conf import settings

from d11 import models as d11_models
from d11.tasks import d11_mviews_rebuild


class AlephCardsFilesExternalStorageServiceException(Exception):
    pass


class AlephCardsFilesExternalStorageService:
    export_instance: d11_models.DocAlephCardFilesExport

    def __init__(self, export_instance: d11_models.DocAlephCardFilesExport):
        self.export_instance = export_instance

    @classmethod
    def make_import_instance_and_do_export(cls, is_all: bool = False) -> Optional[d11_models.DocAlephCardFilesExport]:
        export_instance = cls.make_export_instance(is_all=is_all)
        if not export_instance:
            return
        export_service = cls(export_instance)
        export_service.do_export()
        return export_service.export_instance

    def do_export(self):
        for card in self.export_instance.cards.all():
            if not card.file:
                continue
            path = Path(card.file.path)
            with path.open('rb') as f:
                self.connection.storeFile(settings.ALEPH_CARDS_EXTERNAL_STORAGE_DIRNAME, path.name, f)

    @classmethod
    @transaction.atomic
    def make_export_instance(cls, is_all: bool = False) -> Optional[d11_models.DocAlephCardFilesExport]:
        d11_mviews_rebuild()
        queryset = d11_models.DocAlephCard.objects.filter(file__isnull=False)
        if not is_all:
            queryset = queryset.exclude(files_exports__isnull=False)
        if not queryset.exists():
            return
        instance = d11_models.DocAlephCardFilesExport(is_all=is_all)
        instance.save()
        instance.cards.add(*queryset.values_list('id', flat=True))
        return instance

    @property
    def connection(self) -> SMBConnection:
        key = '_connection'
        if not hasattr(self, key):
            my_name = socket.gethostname()
            remote_name = settings.ALEPH_CARDS_EXTERNAL_STORAGE_NETWORK_NAME
            remote_port = settings.ALEPH_CARDS_EXTERNAL_STORAGE_NETWORK_PORT
            username = settings.ALEPH_CARDS_EXTERNAL_STORAGE_USER_NAME
            password = settings.ALEPH_CARDS_EXTERNAL_STORAGE_USER_PASSWORD
            connection = SMBConnection(username, password, my_name, remote_name)
            try:
                assert connection.connect(remote_name, port=remote_port), True
            except AssertionError:
                raise AlephCardsFilesExternalStorageServiceException('Is not connected')
            except Exception as e:
                raise AlephCardsFilesExternalStorageServiceException(str(e))
            setattr(self, key, connection)
        return getattr(self, key)
