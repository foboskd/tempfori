import re
import json
from pathlib import Path

from django.conf import settings

from d11.serializers.aleph import (
    DocAlephCardAbstract,
    DocAlephCardSynopsisAbstract,
    DocAlephCardDissertationAbstract,
    DocAlephSerializerAbstract
)


class DocVakAlephCard(DocAlephCardAbstract):
    def __post__init__(self):
        super().__post__init__()
        self._data_prepare()
        self._data_patch_by_card()

    def _data_prepare(self):
        re_space_less = re.compile(r'\s+')
        full_name = self.doc.get_value_by_name('full_name')
        full_name_bits = full_name.split()
        specialty_code_bits = self.doc.get_value_by_name('specialty_code').split()
        specialty_code = specialty_code_bits[0]
        specialty_name = ' '.join(specialty_code_bits[2:])
        city_name = None
        defense_date = self.doc.get_value_by_name('defense_date')
        if self.doc.get_value_by_name('address'):
            city_name = self.doc.get_value_by_name('address').split(',')[0].replace('г.', '').strip()
        place_name = None
        if self.doc.get_value_by_name('place_name'):
            place_name = re_space_less.sub(" ", self.doc.get_value_by_name('place_name'))
        council_code = self.doc.get_value_by_name('council_code')
        self.data.update({
            '003': 'RuMoRGB',
            '040': {
                'a': 'RuMoRGB',
                'b': 'rus',
                'c': 'RuMoRGB',
            },
            '0410': {
                'a': 'rus',
            },
            '072 7': {
                'a': specialty_code,
                2: 'nsnr',
            },
            '1001': {
                'a': f'{full_name_bits[0]}, %s' % ' '.join(full_name_bits[1:]),
            },
            '24500': {
                'a': f'{self.doc.get_value_by_name("subject")} :',
                'b': f' ... {self.doc.get_value_by_name("kind_aleph") or self.doc.get_value_by_name("kind")}'
                     f' {self.doc.get_value_by_name("industry_aleph") or self.doc.get_value_by_name("industry")}'
                     f' : {specialty_code}',
                'c': f'{full_name};'
                     f' [Место защиты: {place_name} ; Диссовет {council_code}]',
            },
            '260': {
                'a': city_name,
                'c': self.doc.get_value_by_name('defense_date').year,
            },
            '5411': {
                'b': self.doc.url,
                'c': f'D11-{self.doc.id}',
                'd': self.doc.created_at.strftime('%Y%m%d'),
                'e': defense_date.strftime('%Y.%m.%d'),
            },
            '650 7': {
                'a': specialty_name,
                '2': 'nsnr',
            },
            '7202': {
                'a': f'{place_name} ; Диссовет {council_code}',
            },
            '911': {
                'a': 'D11',
                'b': self.doc.id,
            },
            'OWN': {
                'a': 'RSL',
            },
        })

    def _data_patch_by_card(self):
        if self.aleph_card:
            self.data.update({
                '001': self.aleph_card_id,
                '85641': {
                    'q': 'application/pdf',
                    'u': f'http://dlib.rsl.ru/{Path(*self.aleph_card.file_path.parts[1:])}',
                },
            })
            if self.aleph_card.aleph_fields_json:
                self.data.update(self.aleph_card.aleph_fields_json)
            if '85641' in self.data and 'y' not in self.data['85641']:
                self.data['85641']['y'] = 'Читать'


class DocVakAlephCardSynopsis(DocVakAlephCard, DocAlephCardSynopsisAbstract):
    def _data_prepare(self):
        super()._data_prepare()
        self.data['008'] = f'210330s{self.doc.get_value_by_name("publication_date").year}^^^^ru^||||^^a^^^^|00^u^rus^d'
        self.data['017'] = {'a': '', 'b': ''}
        self.data['24500']['b'] = 'автореферат дис. %s' % self.data['24500']['b']
        self.data['300'] = {'a': 'с.', 'b': ''}
        self.data['911']['c'] = 'autoref'
        self.data['979'] = [
            {'a': self.data['911']['c']},
            {'a': 'dlopen'},
        ]


class DocVakAlephCardDissertation(DocVakAlephCard, DocAlephCardDissertationAbstract):
    def _data_prepare(self):
        super()._data_prepare()
        self.data['008'] = f'210330s{self.doc.get_value_by_name("defense_date").year}^^^^ru^||||^^m^^^^|00^u^rus^d'
        self.data['017'] = {'a': 'д', 'b': 'RuMoRGB'}
        self.data['24500']['b'] = 'диссертация %s' % self.data['24500']['b']
        self.data['300'] = {'a': 'с.', 'b': 'ил.'}
        # self.data['500'] = {'a': 'Предзащита'}
        self.data['504'] = {'a': 'Библиогр.: с.'}
        self.data['911']['c'] = 'disser'
        self.data['979'] = [
            {'a': self.data['911']['c']},
            {'a': 'dllocal'},
        ]
        synopsis = self.doc.get_cards_dict().get('synopsis')
        if synopsis:
            self.data['LKR'] = {
                'a': 'PAR',
                'b': synopsis.aleph_id,
                'l': settings.ALEPH_IMPORT_ALEPH_ID_SUFFIX,
                'm': 'Диссертация',
                'n': 'Автореферат'
            }


class DocVakAlephSerializer(DocAlephSerializerAbstract):
    @property
    def synopsis(self) -> DocVakAlephCardSynopsis:
        return DocVakAlephCardSynopsis(self.doc, **self.kwargs)

    @property
    def dissertation(self) -> DocVakAlephCardDissertation:
        return DocVakAlephCardDissertation(self.doc, **self.kwargs)
