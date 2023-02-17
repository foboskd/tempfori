import json
from typing import Dict

from pymarc import MARCReader, Record, Field


class AlephSequentialReader(MARCReader):
    def __init__(self, marc_target):
        super(AlephSequentialReader, self).__init__(marc_target)

    def __next__(self):
        """
        To support iteration.
        """
        record_data = ''
        line = self.file_handle.readline()
        if not line:
            raise StopIteration
        key = line[0:9]
        current_key = key

        while key == current_key:
            record_data += line
            position = self.file_handle.tell()
            line = self.file_handle.readline()
            key = line[0:9]

        self.file_handle.seek(position)
        record = AlephSequentialRecord(record_data)
        return record


class AlephSequentialRecord(Record):
    def __init__(self, data='', ):
        self.leader = (' ' * 10) + '22' + (' ' * 8) + '4500'
        self.fields = list()
        self.pos = 0
        if len(data) > 0:
            self.decode_aleph(data)

    def decode_aleph(self, data):
        self.aleph_id = data[0:9]
        lines = data.splitlines()
        for line in lines:
            tag = line[10:13]
            ind1 = line[13:14]
            ind2 = line[14:15]
            rest = line[18:]
            if tag == 'FMT':
                self.aleph_format = rest[:2]
            elif tag == 'LDR':
                self.leader = rest
            elif tag < '010':
                self.add_field(Field(tag=tag, data=rest))
            else:
                subfields = list()
                subfield_data = rest.split('$$')
                if len(subfield_data) == 1:
                    self.add_field(Field(tag=tag, indicators=[ind1, ind2], subfields=['', rest]))
                else:
                    subfield_data.pop(0)
                    for subfield in subfield_data:
                        subfields.extend([subfield[0], subfield[1:]])
                    self.add_field(Field(tag=tag, indicators=[ind1, ind2], subfields=subfields))

    def encode_aleph(self):
        """To be implemented"""
        raise NotImplementedError

    def get(self, item: str):
        return self

    def as_d11_dict(self) -> Dict:
        result = {}
        for field in self.as_dict()['fields']:
            for field_id, field_value in field.items():
                if isinstance(field_value, str):
                    result_field_id = field_id
                    result_field_value = field_value
                else:
                    result_field_id = field_id
                    ind1 = field_value['ind1'].strip()
                    ind2 = field_value['ind2'].strip()
                    if ind2:
                        result_field_id = result_field_id + (ind1 or ' ') + ind2
                    elif ind1:
                        result_field_id = result_field_id + ind1
                    result_field_value = {}
                    for subfield in field_value['subfields']:
                        for subfield_k, subfield_v in subfield.items():
                            if subfield_k == '':
                                result_field_value = subfield_v
                                break
                            result_field_value[subfield_k] = subfield_v
                if result_field_id not in result:
                    result[result_field_id] = []
                result[result_field_id].append(result_field_value)
        for k, v in result.items():
            if isinstance(v, list) and len(v) == 1:
                result[k] = v[0]
        return result
