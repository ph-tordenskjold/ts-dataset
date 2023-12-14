import abc
import json
import os

import jsonschema

from tsdataset import settings, BBox


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

    def crop(self, x1, y1, x2, y2) -> 'TsAnnotation':
        bbox = BBox(**{'x1': x1, 'y1': y1, 'x2': x2, 'y2': y2})
        cropped_annotations = []
        data = self.data.copy()
        data["annotations"] = []
        data["i"] = x1
        data["j"] = y1
        for annotation in self.data["annotations"]:
            b = BBox(**annotation)
            if b.intersects(bbox):
                ibox = b.get_intersecting_box(bbox).reference(x1, y1)
                data['annotations'].append({
                    **ibox.bbox_dict,
                    **ibox.meta,
                })
                cropped_annotations.append(annotation)
        return TsAnnotation(json_data=data)

    @property
    def bboxes(self):
        return [BBox(**d) for d in self.data['annotations']]

    @property
    def images(self):
        return self.data['images']

    def __len__(self):
        return len(self.bboxes)

    def dump(self, image_name: str):
        return json.dumps([{
            "image": image_name,
            "annotations": [
                {'label': a['class'],
                 'coordinates': {'x': a['x'], 'y': a['y'], 'width': a['w'], 'height': a['h']}}
                for a in self.data["annotations"]]
        }], indent=4).encode('utf-8')


class TsMTD(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data=json_data)
        self._schema = 'mtd_schema.json'

    @property
    def annotations(self):
        return self.data['annotations']

    def __len__(self):
        return len(self.data['annotations'])
