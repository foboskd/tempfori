from abc import abstractmethod
from typing import Dict, Optional

from d11.serializers import DocSerializerAbstract

from d11.models.doc import Doc
from d11.models.doc_aleph import DocAlephCard, DocAlephCardKind


class DocAlephCardAbstract:
    doc: 'Doc'
    data: Dict = {}
    kwargs: Dict = {}

    DOC_ALEPH_CARD_KIND: Optional[str] = None

    doc_row_index: Optional[str] = None

    def __init__(self, doc: 'Doc', doc_row_index: Optional[str] = None, data: Optional[Dict] = None, **kwargs):
        self.doc = doc
        self.doc_row_index = doc_row_index
        self.data = data or {}
        self.kwargs = kwargs
        self.__post__init__()

    def __post__init__(self):
        ...

    def __str__(self):
        ret = [
            self.row_to_string('FMT', 'BK'),
            self.row_to_string('LDR', '^^^^^nam^a22^^^^^7^^4500'),
        ]
        for k, v in sorted(self.data.items(), key=self.sort_fields):
            if not isinstance(v, (list, tuple)):
                v = [v]
            for vv in v:
                if isinstance(vv, str):
                    ret.append(self.row_to_string(k, vv))
                else:
                    ret.append(
                        self.row_to_string(
                            k,
                            '$$%s' % '$$'.join(
                                f'{kk}{vvv}'
                                for kk, vvv in sorted(vv.items(), key=self.sort_subfields)
                            )
                        )
                    )
        ret = '\n'.join(ret)
        return ret

    def row_to_string(self, field: str, value: str):
        row_id = str(self.aleph_card_id or self.doc_row_index or 0).zfill(9)
        return f'{row_id} {field.ljust(5)} L {value}'

    @classmethod
    def sort_fields(cls, item) -> str:
        try:
            str(int(item[0].split(' ')[0]))
            return '!%s' % item[0]
        except ValueError:
            return item[0]

    @classmethod
    def sort_subfields(cls, item) -> str:
        try:
            return str(int(item[0]))
        except ValueError:
            return '!%s' % item[0]

    @property
    def aleph_card(self) -> Optional[DocAlephCard]:
        key = '_aleph_card'
        if not hasattr(self, key):
            for aleph_card in self.doc.aleph_cards.all():
                if aleph_card.kind == self.DOC_ALEPH_CARD_KIND:
                    setattr(self, key, aleph_card)
                    break
        return getattr(self, key, None)

    @property
    def aleph_card_id(self) -> Optional[str]:
        if self.aleph_card:
            return self.aleph_card.aleph_id


class DocAlephCardSynopsisAbstract(DocAlephCardAbstract):
    DOC_ALEPH_CARD_KIND = DocAlephCardKind.SYNOPSIS


class DocAlephCardDissertationAbstract(DocAlephCardAbstract):
    DOC_ALEPH_CARD_KIND = DocAlephCardKind.DISSERTATION


class DocAlephSerializerAbstract(DocSerializerAbstract):
    @property
    @abstractmethod
    def synopsis(self) -> DocAlephCardSynopsisAbstract:
        ...

    @property
    @abstractmethod
    def dissertation(self) -> DocAlephCardDissertationAbstract:
        ...
