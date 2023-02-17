from typing import TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from d11.models import Doc


class DocSerializerAbstract:
    doc: 'Doc'
    kwargs: Dict

    def __init__(self, doc: 'Doc', **kwargs):
        self.doc = doc
        self.kwargs = kwargs
        self.__post__init__()

    def __post__init__(self):
        ...
