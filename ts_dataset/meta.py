import abc
import json
import os

import jsonschema

from ts_dataset import settings


class TsJson(abc.ABC):

    def __init__(self, json_data: dict = None):
        if json_data is None:
            json_data = {}
        self._data = json_data
        self._schema = None

    @classmethod
    def load(cls, json_file_path):
        with open(json_file_path) as file:
            json_data = json.load(file)
        return cls(json_data)

    def validate(self):
        with open(os.path.join(settings.BASE_DIR, 'schema', self._schema)) as file:
            schema = json.load(file)
            jsonschema.validate(instance=self.data, schema=schema)
        return self

    def __eq__(self, other):
        return self.data == other.data

    def __repr__(self):
        return f"{self.data}"

    def __str__(self):
        return f"{self.data}"

    @property
    def data(self):
        return self._data


class TsAnnotation(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data)
        self._schema = 'annotation_schema.json'


class TsMTD(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data=json_data)
        self._schema = 'mtd_schema.json'
