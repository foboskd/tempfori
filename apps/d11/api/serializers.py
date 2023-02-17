from rest_framework import serializers

from d11 import models as d11_models

from project.contrib.drf.fields import PrimaryKeyRelatedIdField
from project.contrib.drf.serializers import ModelSerializerWithCallCleanMethod


class SourceSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.Source
        fields = ['id', 'label']


class RefSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.Ref
        fields = '__all__'


class DocFieldSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.DocField
        fields = '__all__'


class DocFieldValueSerializer(ModelSerializerWithCallCleanMethod):
    doc_id = PrimaryKeyRelatedIdField(queryset=d11_models.Doc.objects)
    field_id = PrimaryKeyRelatedIdField(queryset=d11_models.DocField.objects)
    field_name = serializers.CharField(source='field.name')
    field_label = serializers.CharField(source='field.label')
    field_type = serializers.CharField(source='field.type')

    class Meta:
        model = d11_models.DocFieldValue
        fields = ['id', 'doc_id', 'field_id', 'field_name', 'field_label', 'field_type', 'value']


class DocFileValueSerializer(DocFieldValueSerializer):
    class Meta(DocFieldValueSerializer.Meta):
        model = d11_models.DocFileValue


class DocAlephCardSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.DocAlephCard
        exclude = ['doc']


class DocAdvancedAttributesSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.DocAdvancedAttributes
        exclude = ['doc']


class DocFullNameDoublesSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.DocFullNameDoubles
        exclude = ['doc', 'full_name']


class DocSerializer(ModelSerializerWithCallCleanMethod):
    class Meta:
        model = d11_models.Doc
        fields = [
            'last_date_abis_manual_changes', 'is_checked', 'is_sync_synopsis_to_abis',
            'is_sync_dissertation_to_abis', 'is_track_external',
        ]


class DocReadListSerializer(DocSerializer):
    source_id = PrimaryKeyRelatedIdField(queryset=d11_models.Source.objects)
    source = SourceSerializer()
    advanced_attributes = DocAdvancedAttributesSerializer()

    class Meta(DocSerializer.Meta):
        fields = [
            *['id', 'source_id', 'url', 'source', 'content_file', 'content_file_hash'],
            *DocSerializer.Meta.fields,
            *['advanced_attributes']
        ]


class DocReadSerializer(DocReadListSerializer):
    fields_values = DocFieldValueSerializer(many=True)
    files_values = DocFileValueSerializer(many=True)
    aleph_cards = DocAlephCardSerializer(many=True)
    full_name_doubles = DocFullNameDoublesSerializer()

    class Meta(DocReadListSerializer.Meta):
        fields = [
            *DocReadListSerializer.Meta.fields,
            *['fields_values', 'files_values', 'aleph_cards', 'full_name_doubles'],
        ]
