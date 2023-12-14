import json
import os
import uuid
import zipfile
from pathlib import Path

from tsdataset.meta import TsAnnotation, TsMTD

""" Usage example:

with TsDatasetBuilder(name='test', folder=folder) as builder:
    for raster_path in paths:
        bboxes = get_bboxes()
        with rasterio.open(raster_path) as raster:
            for i in range(0, raster.width, step_size):
                for j in range(0, raster.height, step_size):
                    window_box = ts_dataset.BBox(**{'x1': i, 'y1': j, 'x2': i + step_size, 'y2': j + step_size})
                    intersecting_bboxes = [bbox for bbox in bboxes if bbox.intersects(window_box)]
                    if any(intersecting_bboxes):
                        with builder.new_annotation(scene.identifier) as annotation_builder:
                            cropped_raster = raster.read(window=Window(i, j, step_size, step_size))
                            cbox = ts_dataset.BBox(**{'x1': i, 'y1': j,
                                                  'w': cropped_raster.shape[-1],
                                                  'h': cropped_raster.shape[-2]})
                            for bbox in intersecting_bboxes:
                                if bbox.intersects(cbox):
                                    bbox = bbox.get_intersecting_box(cbox).reference(i, j)
                                    annotation_builder.add_bbox(**{**bbox.bbox_dict, **bbox.meta})
                            annotation_builder.add_property(
                                        **{'scene_name': scene.name, 'scene_id': scene.identifier,
                                           'timestamp': scene.timestamp.isoformat(),
                                           'i': i, 'j': j, 'width': cropped_raster.shape[-1],
                                           'height': cropped_raster.shape[-2]})
                            with NamedTemporaryFile(suffix='.npy') as tmp:
                                numpy.save(tmp, cropped_raster[0])
                                annotation_builder.add_image(tmp, 'cross')
                            with NamedTemporaryFile(suffix='.npy') as tmp:
                                numpy.save(tmp, cropped_raster[1])
                                annotation_builder.add_image(tmp, 'co')
"""


class TsDatasetBuilder:
    class TsAnnotationBuilder:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            TsAnnotation(json_data=self._annotation).validate()
            self._zip_file.writestr(self._annotation_path, json.dumps(self._annotation, indent=4).encode('utf-8'))

        def __init__(self, zip_file: zipfile.ZipFile, folder: str):
            self._images_path = os.path.join(folder, 'images')
            self._annotation_id = str(uuid.uuid4()) + '.json'
            self._annotation_path = os.path.join(folder, 'annotations', self._annotation_id)
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
        self._zip_file = zipfile.ZipFile(self._zip_path, 'w', zipfile.ZIP_DEFLATED)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        labels = set(self._labels)
        mapping = {'n_labels': len(labels), 'labels': {}}
        for i, label in enumerate(labels):
            mapping['labels'][label] = i
        self._mtd.update(**mapping)
        TsMTD(json_data=self._mtd).validate()
        self._zip_file.writestr('mtd.json', json.dumps(self._mtd, indent=4).encode('utf-8'))
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
