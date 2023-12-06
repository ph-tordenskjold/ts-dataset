import io
import json
import os
import uuid
import zipfile
from pathlib import Path

from ts_dataset.meta import TsAnnotation, TsMTD


def _write_to_zip(zip_file, data, name):
    buffer = io.BytesIO()
    buffer.write(data)
    zip_file.writestr(name, buffer.getvalue())
    buffer.close()


class TsDatasetBuilder:
    class TsAnnotationBuilder:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            TsAnnotation(json_data=self._annotation).validate()
            self._zip_file.writestr(self._annotation_path, json.dumps(self._annotation))

        def __init__(self, zip_file: zipfile.ZipFile, folder: str):
            self._images_path = os.path.join(folder, 'images')
            self._annotation_id = str(uuid.uuid4()) + '.json'
            self._annotation_path = os.path.join(folder, 'annotations', str(uuid.uuid4()) + '.json')
            self._metas_path = os.path.join(folder, 'meta')
            self._look_path = os.path.join(folder, 'look')

            self._zip_file = zip_file
            self._annotation = {
                "annotations": [],
                "images": {},
                "meta": {},
                "tags": [],
            }

        def add_look(self, file, name: str):
            abs_name = os.path.join(self._look_path, name)
            self._zip_file.write(file, abs_name)
            self._annotation['look'] = abs_name

        def add_image(self, file, name: str):
            abs_name = os.path.join(self._images_path, str(uuid.uuid4()) + str(Path(file.name).suffix))
            self._zip_file.write(file.name, abs_name)
            self._annotation['images'][name] = abs_name

        def add_meta(self, file, name: str):
            abs_name = os.path.join(self._metas_path, str(uuid.uuid4()) + Path(file.name).suffix)
            self._zip_file.write(file, abs_name)
            self._annotation['meta'][name] = abs_name

        def add_bbox(self, **kwargs):
            self._annotation["annotations"].append(kwargs)

        def add_property(self, **kwargs):
            self._annotation.update(kwargs)

        def add_tag(self, tag: str):
            self._annotation['tags'].append(tag)

    def __init__(self, name: str = "TsDataset", folder: str = None):
        self._name = name
        self._zip_path = (name if folder is None else os.path.join(folder, name)) + '.zip'
        self._folder = folder
        self._mtd = {"annotations": []}
        self._zip_file = None
        self._labels = []

    def add_label(self, label: str):
        self._labels.append(label)

    def __enter__(self):
        self._zip_file = zipfile.ZipFile(self._zip_path, 'w')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        labels = set(self._labels)
        mapping = {'n_labels': len(labels), 'labels': {}}
        for i, label in enumerate(labels):
            mapping['labels'][label] = i
        self._mtd.update(**mapping)
        TsMTD(json_data=self._mtd).validate()
        _write_to_zip(self.zip_file, json.dumps(self._mtd).encode('utf-8'), 'mtd.json')
        self.zip_file.close()

    def new_annotation(self, folder: str = str(uuid.uuid4())):
        annotation_builder = self.TsAnnotationBuilder(self.zip_file, folder=folder)
        self._mtd["annotations"].append(annotation_builder._annotation_path)
        return annotation_builder

    @property
    def name(self):
        return self._name

    @property
    def folder(self):
        return self._folder

    @property
    def zip_file(self) -> zipfile.ZipFile:
        return self._zip_file
