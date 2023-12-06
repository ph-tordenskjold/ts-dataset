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

    @property
    def data(self):
        return self._data


class TsAnnotation(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data)
        self._schema = 'annotation_schema.json'

    def crop(self, x1, y1, x2, y2) -> 'TsAnnotation':  # TODO add tests
        data = self.data.copy()
        annotations = data["annotations"]
        cropped_annotations = []
        for annotation in annotations:
            x, y, w, h = annotation["x"], annotation["y"], annotation["w"], annotation["h"]
            x = max(0, min(x - x1, x2 - x1))
            y = max(0, min(y - y1, y2 - y1))
            w = min(x2 - x1 - x, w)
            h = min(y2 - y1 - y, h)
            if w > 0 and h > 0:
                annotation["x"] = x
                annotation["y"] = y
                annotation["w"] = w
                annotation["h"] = h
                cropped_annotations.append(annotation)
        data["annotations"] = cropped_annotations
        data["i"] = x1
        data["j"] = y1
        return TsAnnotation(json_data=data)

    def dump(self, image_name: str):
        return json.dumps([{
            "image": image_name,
            "annotations": [
                {'label': a['class'],
                 'coordinates': {'x': a['x'], 'y': a['y'], 'width': a['w'], 'height': a['h']}}
                for a in self.data["annotations"]]
        }], indent=4)


class TsMTD(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data=json_data)
        self._schema = 'mtd_schema.json'
