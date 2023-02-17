import re
from abc import abstractmethod

from django.db.models import Q
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from django.views.generic import DetailView, ListView

from d11.models import Doc

RESPONSE_CONTENT_TYPE_HTML = 'text/html; charset=utf-8'
RESPONSE_CONTENT_TYPE_TEXT = 'text/text; charset=utf-8'


def get_doc_queryset() -> Doc.QuerySet:
    return Doc.objects.prefetch_related('source', 'fields_values', 'fields_values__field')


class DocView(DetailView):
    queryset = get_doc_queryset()
    response_content_type = RESPONSE_CONTENT_TYPE_HTML

    def get_content(self) -> str:
        rows = [
            ['id', self.object.id],
            ['source', self.object.source],
            ['url', self.object.url],
            ['aleph_synopsis_id', self.object.aleph_synopsis_id],
            ['aleph_synopsis_id_date', self.object.aleph_synopsis_id_date],
            ['aleph_dissertation_id', self.object.aleph_dissertation_id],
            ['aleph_dissertation_id_date', self.object.aleph_dissertation_id_date],
            ['created_at', self.object.created_at],
            ['updated_at', self.object.updated_at],
            '&nbsp;',
        ]
        for value in self.object.fields_values.all():
            rows.append([
                f'{value.field.label}<br><i>{value.field.name or "&mdash;"}</i>',
                re.sub(r'\s+', ' ', str(value.python_value) or '')
            ])

        s = []
        for row in rows:
            if isinstance(row, list):
                s.append(f'<td><b>{row[0]}</b></td><td>{row[1] or ""}</td>')
            else:
                s.append('<td colspan=2>%s</td>' % row)
        return mark_safe('<table border=1 cellpadding=5 cellspacing=0><tr>%s</tr></table>' % '</tr><tr>'.join(s))

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(
            content=self.get_content(),
            content_type=self.response_content_type,
        )


class DocAlephTxtBaseView(DocView):
    response_content_type = RESPONSE_CONTENT_TYPE_TEXT
    serializer_property_name: str

    def get_content(self) -> str:
        return str(getattr(self.object.get_serializer_aleph(), self.serializer_property_name))


class DocAlephTxtSynopsisView(DocAlephTxtBaseView):
    serializer_property_name = 'synopsis'


class DocAlephTxtDissertationView(DocAlephTxtBaseView):
    serializer_property_name = 'dissertation'


class DocAlephTxtBaseListView(ListView):
    response_content_type = RESPONSE_CONTENT_TYPE_TEXT
    queryset = get_doc_queryset()
    serializer_property_name: str = ''
    view_mode: str = ''

    def get_queryset(self) -> Doc.QuerySet:
        queryset = self.filter_queryset_by_view_mode(super().get_queryset())
        if limit := self.request.GET.get('limit'):
            queryset = queryset[:int(limit)]
        return queryset

    def get_content(self) -> str:
        doc_index = 0
        content = []
        for doc in self.object_list:
            if self.serializer_property_name:
                aleph_id = getattr(doc, f'aleph_{self.serializer_property_name}_id')
                if self.view_mode == 'create' and aleph_id is not None:
                    continue
                if self.view_mode == 'update' and aleph_id is None:
                    continue
                doc_index += 1
                content.append(self.get_doc_content(doc, doc_index, self.serializer_property_name))
            else:
                for serializer_property_name in ['synopsis', 'dissertation']:
                    aleph_id = getattr(doc, f'aleph_{serializer_property_name}_id')
                    if self.view_mode == 'create' and aleph_id is not None:
                        continue
                    if self.view_mode == 'update' and aleph_id is None:
                        continue
                    doc_index += 1
                    content.append(self.get_doc_content(doc, doc_index, serializer_property_name))
        return '\n'.join(content)

    @classmethod
    def get_doc_content(cls, row: Doc, doc_index: int, serializer_property_name: str) -> str:
        return str(getattr(
            row.get_serializer_aleph(doc_index=str(doc_index)),
            serializer_property_name
        ))

    def filter_queryset_by_view_mode(self, queryset: Doc.QuerySet) -> Doc.QuerySet:
        if self.serializer_property_name:
            return queryset.filter(
                self.get_queryset_filter_by_aleph_id_isnull(f'aleph_{self.serializer_property_name}_id')
            )
        return queryset.filter(
            self.get_queryset_filter_by_aleph_id_isnull('aleph_synopsis_id')
            | self.get_queryset_filter_by_aleph_id_isnull('aleph_dissertation_id')
        )

    def get_queryset_filter_by_aleph_id_isnull(self, aleph_id_field_name: str) -> Q:
        id_isnull = True if self.view_mode == 'create' else False
        return Q(**{f'{aleph_id_field_name}__isnull': id_isnull})

    def render_to_response(self, context, **response_kwargs):
        return HttpResponse(
            content=self.get_content(),
            content_type=self.response_content_type,
        )


class DocAlephTxtSynopsisListView(DocAlephTxtBaseListView):
    serializer_property_name = 'synopsis'


class DocAlephTxtDissertationListView(DocAlephTxtBaseListView):
    serializer_property_name = 'dissertation'
