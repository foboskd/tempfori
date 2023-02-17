from typing import TYPE_CHECKING, List, Optional
import re
import magic
import shutil
import hashlib
import logging
import datetime
import requests
import psycopg2
from pathlib import Path
from abc import ABC, abstractmethod
from math import ceil
from urllib.parse import quote

from bs4 import BeautifulSoup
from requests import Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from dateutil.parser import ParserError as DateParserError
from django.db import transaction
from django.conf import settings
from urllib3 import Retry

from project.contrib.datetime import date_parse
from d11.collector import registry, CollectorAbstract, CollectorItemFieldValue, CollectorItem
from d11.serializers.aleph.vak import DocVakAlephSerializer
from d11.tasks import d11_call_collector_method
from d11.models.doc import Doc, DocField, DocFieldType, DocFieldValue, DocFileValue
from d11.models.collector import CollectorImport
from d11.models.ref import RefType, Ref

if TYPE_CHECKING:
    from d11.models.source import Source

__all__ = [
    'CollectorVakAdvert',
    'CollectorVakIndependent',
]

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logger = logging.getLogger(__name__)

mime = magic.Magic(mime=True)


class CollectorVakBase(CollectorAbstract, ABC):
    vak_name: str
    date_from: datetime.date
    date_to: datetime.date
    is_async: bool
    base_url = settings.EXTERNAL_SOURCE_VAK_BASE_URL
    doc_serializer_aleph_class = DocVakAlephSerializer

    http_client_headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/91.0.4472.114 Safari/537.36',
    }

    file_disser_ext_filed_label = 'Интернет-адрес текста диссертации на сайте организации'
    file_autoref_ext_filed_label = 'Интернет-адрес текста автореферата на сайте организации'
    file_autoref_filed_label = 'Автореферат'

    files_collected_tmp_dir = Path(settings.MEDIA_ROOT) / '_collector_files'

    kind_field_label = 'Тип диссертации'
    industry_field_label = 'Отрасль науки'

    def __init__(
            self,
            source: 'Source',
            date_from: Optional[datetime.date] = None,
            date_to: Optional[datetime.date] = None,
            is_async: bool = False,
            **kwargs
    ):
        super().__init__(source, **kwargs)
        self.date_from = date_from
        self.date_to = date_to
        if not self.date_from:
            self.date_from = max(datetime.date.today(), settings.EXTERNAL_SOURCE_VAK_START_FROM_DATE)
        if self.date_from < settings.EXTERNAL_SOURCE_VAK_START_FROM_DATE:
            raise Exception(f'ВАК надо начинать с даты {settings.EXTERNAL_SOURCE_VAK_START_FROM_DATE}')
        if not self.date_to:
            self.date_to = self.date_from
        self.is_async = is_async

    def start(self) -> None:
        import_instance = self.get_or_create_import_instance()
        page_size = 20
        count = self.get_total_count()
        url = self.get_list_url()
        logger.info(f'Import {self.date_from.strftime("%Y-%m-%d")} – {self.date_to.strftime("%Y-%m-%d")} :: '
                    f'Total count: {count}')
        import_instance.extra = {
            'date_from': str(self.date_from),
            'date_to': str(self.date_from),
            'total_count': count,
            'docs_created': 0,
            'docs_updated': 0,
        }
        import_instance.save()
        for i in range(ceil(count / page_size) + 1):
            page_url = url + '&args[]=' + quote('OFFSET:%s' % (i * 20))
            for item_link in self._get_items_urls_from_list_content(self._get_url_content(page_url)):
                fnc = d11_call_collector_method
                if self.is_async:
                    fnc = fnc.delay
                fnc(self, 'do_item', url=item_link, import_instance_id=import_instance.id)

    def get_total_count(self, **kwargs) -> int:
        url = self.get_list_total_count_url()
        return int(self._get_url_content(url))

    @transaction.atomic
    def do_item(self, url: str, import_instance_id: Optional[int] = None, force: bool = False) -> bool:
        doc_kwargs = {
            'url': url,
            'source': self.source,
        }
        doc = Doc.objects.filter(**doc_kwargs).first()
        is_doc_created = False
        is_doc_updated = False
        if not doc:
            is_doc_created = True
            doc = Doc(**doc_kwargs)
            doc.save()
        content = self._get_url_content(url, nocache=force)
        content_hash = hashlib.md5(content.encode()).hexdigest()
        if doc.content_file_hash == content_hash and not force:
            return False
        doc.content_file_hash = content_hash
        doc.content_file.name = Doc._meta.get_field('content_file').generate_filename(doc, '1.html')
        doc_content_file_path = Path(doc.content_file.path)
        doc_content_file_path.parent.mkdir(parents=True, exist_ok=True)
        doc_content_file_path.write_text(content)
        doc.save()
        item = self.get_collector_item_from_content(url, content)
        is_doc_need_save = False
        for item_field in item.fields_values:
            doc_field = DocField.objects.get_by_label(item_field.label)
            if not doc_field:
                sid = transaction.savepoint()
                try:
                    doc_field = DocField.objects.create(label=item_field.label, type=item_field.type)
                    transaction.savepoint_commit(sid)
                except psycopg2.errors.UniqueViolation:
                    transaction.savepoint_rollback(sid)
            doc_field_kwargs = dict(doc=doc, field=doc_field)
            doc_field_value_model = DocFieldValue
            if doc_field.type == DocFieldType.FILE:
                doc_field_value_model = DocFileValue
            if not (doc_field_value := doc_field_value_model.objects.filter(**doc_field_kwargs).first()):
                doc_field_value = doc_field_value_model(**doc_field_kwargs)
            if doc_field_value_model == DocFileValue:
                if doc_field_value.value:
                    continue
                doc_field_value.value = DocFileValue._meta.get_field('value').generate_filename(
                    doc_field_value,
                    f'{doc_field_value.field.name}.pdf'
                )
                doc_field_value_path = Path(doc_field_value.value.path)
                doc_field_value_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(item_field.value, str(doc_field_value_path))
                doc_field_value.save()
                is_doc_updated = True
            elif doc_field_value.value != item_field.value:
                doc_field_value.value = item_field.value
                doc_field_value.save()
                is_doc_updated = True
            if doc_field.name == 'status_color':
                doc.is_track_external = False
                is_doc_need_save = True
            if doc_field.name == 'autoref_file_url' and doc_field_value.value:
                # doc.is_synopsis_exists = True
                is_doc_need_save = True
            if is_doc_need_save:
                doc.save()
        if import_instance_id and (is_doc_created or is_doc_updated):
            import_instance = CollectorImport.objects.select_for_update().get(id=import_instance_id)
            if is_doc_created:
                import_instance.extra['docs_created'] += 1
            if is_doc_updated:
                import_instance.extra['docs_updated'] += 1
            import_instance.save()
            import_instance.docs.add(doc)
        logger.info(url, extra={'fields': len(item.fields_values)})
        return is_doc_created

    def get_collector_item_from_content(self, url: str, content: str) -> CollectorItem:
        soup = BeautifulSoup(content, 'html.parser')
        fields = []
        files_urls = {}
        rows = []
        for row in soup.find('table').find_all('tr'):
            cells = row.find_all('td')
            rows.append(cells)
            if len(cells) < 2:
                continue
            label = cells[0].text.strip()
            if a := cells[1].find('a'):
                value = a.get('href')
                if value.startswith('/'):
                    value = self.base_url + value
                fields.append(
                    CollectorItemFieldValue(label, value)
                )
                if label in [
                    self.file_disser_ext_filed_label,
                    self.file_autoref_ext_filed_label,
                    self.file_autoref_filed_label,
                ]:
                    files_urls[label] = value
            else:
                value = list(cells[1].stripped_strings)
                if not value:
                    continue
                for one_value in value:
                    try:
                        fields.append(
                            CollectorItemFieldValue(label, str(date_parse(one_value).date()), DocFieldType.DATE)
                        )
                    except (DateParserError, OverflowError):
                        fields.append(CollectorItemFieldValue(label, one_value))
                        if label == self.kind_field_label:
                            one_value_cast = Ref.objects.get_by_from_what(RefType.KIND, one_value).to_what
                            label_cast = label + ' (Алеф)'
                            fields.append(CollectorItemFieldValue(label_cast, one_value_cast))
                        if label == self.industry_field_label:
                            one_value_cast = Ref.objects.get_by_from_what(RefType.INDUSTRY, one_value).to_what
                            label_cast = label + ' (Алеф)'
                            fields.append(CollectorItemFieldValue(label_cast, one_value_cast))

        # from terminaltables import SingleTable
        # table = SingleTable([[url, '']] + [[f.label, f.value] for f in fields])
        # print('\n\n', table.table, '\n\n')
        # exit()
        fields.append(CollectorItemFieldValue('id', url.split('/')[-1], DocFieldType.INT))
        files = {}
        for file_label, file_url in files_urls.items():
            if file_path := self._get_url_file_pdf(file_label, file_url):
                files[file_label] = file_path
        if self.file_autoref_ext_filed_label in files:
            fields.append(CollectorItemFieldValue('Файл автореферата', files[self.file_autoref_ext_filed_label]))
        elif self.file_autoref_filed_label in files:
            fields.append(CollectorItemFieldValue('Файл автореферата', files[self.file_autoref_filed_label]))
        if self.file_disser_ext_filed_label in files:
            fields.append(CollectorItemFieldValue('Файл диссертации', files[self.file_disser_ext_filed_label]))
        if len(rows[-1]) == 1:
            s = str(rows[-1])
            status_color = None
            if 'green' in s:
                status_color = 'green'
            if 'red' in s:
                status_color = 'red'
            if status_color:
                fields.append(CollectorItemFieldValue('Статус', status_color))
                fields.append(CollectorItemFieldValue(
                    'Статус - текст',
                    re.sub(r'(\s)+', '\\1', rows[-1][0].get_text(separator='\n', strip=True))
                ))
        return CollectorItem(url=url, fields_values=fields)

    def _get_items_urls_from_list_content(self, html_content: str) -> List[str]:
        result = []
        soup = BeautifulSoup(html_content, 'html.parser')
        for row in soup.find('div', id=f'filtred_{self.vak_name}').find('table').find_all('tr')[1:]:
            result.append(self.base_url + row.find_all('td')[3].find('a').get('href'))
        return result

    @classmethod
    def _get_url_file_pdf(cls, file_label: str, url: str) -> Optional[Path]:
        key = '%s.%s' % (hashlib.md5(url.encode()).hexdigest(), hashlib.md5(file_label.encode()).hexdigest())
        path = cls.files_collected_tmp_dir / key[:2] / key[2:4] / key
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            return path
        try:
            # r = requests.get(url, verify=False, stream=True)
            r = cls._get_url_response(url, nocache=True, stream=True, retry=10)
            if r.status_code == 200:
                with open(path, 'wb') as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
            if not path.exists() or mime.from_file(str(path)) != 'application/pdf':
                path.unlink(missing_ok=True)
                return
        except Exception:
            return
        return path

    @classmethod
    def _get_url_content(cls, url: str, nocache: bool = False) -> str:
        return cls._get_url_response(url, nocache).text

    @classmethod
    def _get_url_response(cls, url: str, nocache: bool = False, stream: bool = False, retry: int = 100) -> Response:
        cache_key = hashlib.md5(url.encode()).hexdigest()
        if not nocache:
            result = cls._cache_get(cache_key)
            if result:
                return result
        retry_strategy = Retry(
            total=retry,
            backoff_factor=2,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session = requests.Session()
        session.mount('https://', adapter)
        result = session.get(url, headers=cls.http_client_headers, verify=False, stream=stream)
        if not nocache:
            cls._cache_set(cache_key, result)
        return result

    @abstractmethod
    def get_list_url(self) -> str:
        pass

    @abstractmethod
    def get_list_total_count_url(self) -> str:
        pass


@registry.register
class CollectorVakAdvert(CollectorVakBase):
    _verbose_name = 'ВАК :: ОБЪЯВЛЕНИЯ О ЗАЩИТАХ ВАК'
    vak_name = 'advert'
    item_url_prefix = 'advert'

    def get_list_url(self) -> str:
        s = f"{self.base_url}/ais/vak/templates/vak_new/adverts_list.php.t?cmd=T:{self.vak_name}&args[]="
        s += quote(
            "*WHERE (1 = 1) AND ((a.date_zach <= '2018-01-01') OR (EXISTS(SELECT 1 FROM case_organizations co "
            "INNER JOIN case_organizations_to_case cotc ON cotc.organization_id = co.id WHERE "
            "((cotc.organization_type = 'dissertation_execution_org') OR "
            "(cotc.organization_type = 'second_dissertation_execution_org')) AND (cotc.case_id = ext.att_id) ))) "
            "AND (a.date_zach >= ?) AND (a.date_zach <= ?)")
        s += f"&args[]={self.date_from}&args[]={self.date_to}"
        return s

    def get_list_total_count_url(self) -> str:
        s = f"{self.base_url}/az/server/php/counter.php?cmd="
        s += quote("SELECT a1.date_zach AS a__date_zach, a1.sois_fam AS a__sois_fam, a1.sois_imy AS a__sois_imy, "
                   "a1.sois_otch AS a__sois_otch, a1.id AS a__id, a1.name_dis AS a__name_dis FROM  att_advert a1 "
                   "LEFT JOIN ( att_case a2 LEFT JOIN dc3_council a3 ON a2.council_id = a3.id ) ON a1.att_id = a2.id "
                   "WHERE  ( a1.date_publ IS NOT NULL AND a1.date_publ != '1970-01-01' AND a1.date_zach IS NOT NULL "
                   "AND a2.is_deleted IS FALSE AND a2.council_id != 1 AND a3.is_vak AND a1.att_id != 100057747 "
                   "AND a1.version IN ( SELECT  MAX( a4.version) FROM  att_advert a4 WHERE  a4.date_publ IS NOT NULL "
                   "AND a4.id = a1.id) ) AND ((1 = 1) AND (( a1.date_zach <= '2018-01-01') "
                   "OR ( EXISTS( SELECT  1 FROM  case_organizations a5 INNER JOIN case_organizations_to_case a6 ON "
                   "a6.organization_id = a5.id WHERE (( a6.organization_type = 'dissertation_execution_org') "
                   "OR ( a6.organization_type = 'second_dissertation_execution_org')) AND ( a6.case_id = a1.att_id)))) "
                   "AND ( a1.date_zach >= ?) AND ( a1.date_zach <= ?)) ORDER BY  a1.date_zach ASC, a1.sois_fam ASC, "
                   "a1.sois_imy ASC LIMIT 20")
        s += f"&args[0]={self.date_from}&args[1]={self.date_to}"
        return s


@registry.register()
class CollectorVakIndependent(CollectorVakBase):
    _verbose_name = 'ВАК :: САМОСТОЯТЕЛЬНОЕ ПРИСУЖДЕНИЕ СТЕПЕНЕЙ'
    vak_name = 'independent'
    item_url_prefix = 'advert_independent'

    def get_list_url(self) -> str:
        s = f"{self.base_url}/ais/vak/templates/vak_new/adverts_list.php.t?cmd=T:{self.vak_name}&args[]="
        s += quote("*WHERE (1 = 1) AND (a.defend_date >= ?) AND (a.defend_date <= ?)")
        s += f"&args[]={self.date_from}&args[]={self.date_to}"
        return s

    def get_list_total_count_url(self) -> str:
        s = f"{self.base_url}/az/server/php/counter.php?cmd="
        s += quote("SELECT  a1.defend_date AS a__defend_date, a1.last_name AS a__last_name, "
                   "a1.first_name AS a__first_name, a1.middle_name AS a__middle_name, a1.case_id AS a__case_id, "
                   "a1.dissertation_name AS a__dissertation_name FROM adverts a1 LEFT JOIN ( cases a2 LEFT JOIN "
                   "( council_states a3 LEFT JOIN councils a4 ON a3.council = a4.id ) ON a2.council_state = a3.id ) "
                   "ON a1.case_id = a2.id WHERE  ( a1.publication_date IS NOT NULL AND a1.defend_date IS NOT NULL AND "
                   "a1.version IN ( SELECT  MAX( a5.version) FROM  adverts a5 WHERE  a5.publication_date IS NOT NULL "
                   "AND a5.case_id = a1.case_id) AND a4.org_union NOT IN (0,4) ) AND ((1 = 1) AND "
                   "( a1.defend_date >= ?) AND ( a1.defend_date <= ?)) ORDER BY  a1.defend_date ASC, a1.last_name ASC, "
                   "a1.first_name ASC LIMIT 20")
        s += f"&args[0]={self.date_from}&args[1]={self.date_to}"
        return s
