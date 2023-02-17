import logging
from pathlib import Path
from django.conf import settings
from paramiko.client import SSHClient, AutoAddPolicy
from paramiko.sftp_attr import SFTPAttributes
from paramiko.sftp_client import SFTPClient

from d11.models.aleph import ExportToAleph, ImportFromAleph

logger = logging.getLogger(__name__)


class AlephTransportServiceException(Exception):
    pass


class AlephTransportService:
    UPLOAD_DIR = Path(settings.ALEPH_UPLOAD_DIR)

    def __del__(self):
        if hasattr(self, '_sftp'):
            self.sftp.close()
        if hasattr(self, '_ssh'):
            self.ssh.close()

    @property
    def ssh(self) -> SSHClient:
        key = '_ssh'
        if not hasattr(self, key):
            ssh = SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(settings.ALEPH_HOST, username=settings.ALEPH_USER, password=settings.ALEPH_PASSWORD)
            setattr(self, key, ssh)
        return getattr(self, key)

    @property
    def sftp(self) -> SFTPClient:
        key = '_sftp'
        if not hasattr(self, key):
            sftp = self.ssh.open_sftp()
            setattr(self, key, sftp)
        return getattr(self, key)

    def upload_file(self, src: Path, dst: Path) -> SFTPAttributes:
        try:
            self.sftp.stat(str(dst.parent))
        except FileNotFoundError:
            self.sftp.mkdir(str(dst.parent))
        return self.sftp.put(str(src), str(dst))

    def download_file(self, src: Path, dst: Path) -> Path:
        dst.parent.mkdir(parents=True, exist_ok=True)
        self.sftp.get(str(src), str(dst))
        return dst

    def remove_file(self, path: Path) -> None:
        self.sftp.remove(str(path))

    def exec_command(self, cmd: str):
        logger.debug('AlephTransportService.exec_command', extra={'cmd': cmd})
        stdin, stdout, stderr = self.ssh.exec_command(cmd)
        for line in stdout:
            logger.info(line.replace('\n', ''))


class AlephTransportExportService(AlephTransportService):
    export_instance: ExportToAleph

    EXPORT_BOTH_CARDS_CREATE_COMMAND = settings.ALEPH_EXPORT_BOTH_CARDS_CREATE_COMMAND
    EXPORT_SINGLE_CARD_CREATE_COMMAND = settings.ALEPH_EXPORT_SINGLE_CARD_CREATE_COMMAND
    EXPORT_CREATE_RESULT_DIR = Path(settings.ALEPH_EXPORT_CREATE_RESULT_DIR)

    EXPORT_UPDATE_COMMAND = settings.ALEPH_EXPORT_UPDATE_COMMAND
    EXPORT_UPDATE_RESULT_DIR = Path(settings.ALEPH_EXPORT_UPDATE_RESULT_DIR)

    def __init__(self, export_instance: ExportToAleph):
        self.export_instance = export_instance

    def docs_create_both_cards(self) -> None:
        src = Path(self.export_instance.docs_serialized_file.path)
        dst = self.UPLOAD_DIR / f'{self.export_instance.id_verbose}{src.suffix}'
        self.upload_file(src, dst)
        self.exec_command(f'{self.EXPORT_BOTH_CARDS_CREATE_COMMAND} {dst}')
        self.export_instance.result_file.name = str(self.get_docs_create_local_result_file_path(dst))
        result_src = self.get_docs_create_aleph_result_file_path(dst)
        result_dst = Path(self.export_instance.result_file.path)
        self.download_file(result_src, result_dst)
        self.remove_file(dst)
        self.remove_file(result_src)
        self.export_instance.save()

    def docs_create_single_card(self) -> None:
        src = Path(self.export_instance.docs_serialized_file.path)
        dst = self.UPLOAD_DIR / f'{self.export_instance.id_verbose}{src.suffix}'
        self.upload_file(src, dst)
        self.exec_command(f'{self.EXPORT_SINGLE_CARD_CREATE_COMMAND} {dst}')
        self.export_instance.result_file.name = str(self.get_docs_create_local_result_file_path(dst))
        result_src = self.get_docs_create_aleph_result_file_path(dst)
        result_dst = Path(self.export_instance.result_file.path)
        self.download_file(result_src, result_dst)
        self.remove_file(dst)
        self.remove_file(result_src)
        self.export_instance.save()

    def get_docs_create_aleph_result_file_path(self, dst: Path) -> Path:
        return self.EXPORT_CREATE_RESULT_DIR / f'{dst.name}.sysno_id'

    def get_docs_create_local_result_file_path(self, dst: Path) -> Path:
        return ExportToAleph._meta.get_field('result_file').generate_filename(
            self.export_instance,
            str(self.get_docs_create_aleph_result_file_path(dst))
        )

    def docs_update(self) -> None:
        src = Path(self.export_instance.docs_serialized_file.path)
        dst = self.UPLOAD_DIR / f'{self.export_instance.id_verbose}{src.suffix}'
        self.upload_file(src, dst)
        self.exec_command(f'{self.EXPORT_UPDATE_COMMAND} {dst}')
        finished_file = self.get_docs_updated_aleph_finished_file_path(dst)
        try:
            self.sftp.stat(str(finished_file))
        except FileNotFoundError:
            error_msg = 'Docs update result file not found'
            logger.error(error_msg, extra={'instance': self.export_instance})
            raise AlephTransportServiceException(error_msg)

    def get_docs_updated_aleph_finished_file_path(self, dst: Path) -> Path:
        return self.EXPORT_UPDATE_RESULT_DIR / f'{dst.name}.finished'


class AlephTransportImportService(AlephTransportService):
    import_instance: ImportFromAleph

    IMPORT_COMMAND = settings.ALEPH_IMPORT_COMMAND
    IMPORT_RESULT_DIR = Path(settings.ALEPH_IMPORT_RESULT_DIR)

    def __init__(self, import_instance: ImportFromAleph):
        self.import_instance = import_instance

    def docs_import(self):
        src = Path(self.import_instance.docs_serialized_file.path)
        dst = self.UPLOAD_DIR / f'{self.import_instance.id_verbose}{src.suffix}'
        self.upload_file(src, dst)
        self.exec_command(f'{self.IMPORT_COMMAND} {dst}')
        self.import_instance.result_file.name = str(self.get_docs_import_local_result_file_path(dst))
        result_src = self.get_docs_import_aleph_result_file_path(dst)
        result_dst = Path(self.import_instance.result_file.path)
        self.download_file(result_src, result_dst)
        self.remove_file(dst)
        self.remove_file(result_src)
        self.import_instance.save()

    def get_docs_import_aleph_result_file_path(self, dst: Path) -> Path:
        return self.IMPORT_RESULT_DIR / f'{dst.name}.seq'

    def get_docs_import_local_result_file_path(self, dst: Path) -> Path:
        return ImportFromAleph._meta.get_field('result_file').generate_filename(
            self.import_instance,
            str(self.get_docs_import_aleph_result_file_path(dst))
        )
