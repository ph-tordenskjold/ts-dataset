import json
import os
import unittest

import jsonschema.exceptions

from tsdataset import settings
from tsdataset.meta import TsAnnotation


class TestAnnotation(unittest.TestCase):
    annotation_path = os.path.join(settings.TEST_DATA, 'test_dataset1', 'annotation1.json')
    annotation_error_path = os.path.join(settings.TEST_DATA, 'annotation_error.json')
    with open(annotation_path) as f:
        annotation1 = json.load(f)

    def test_init_TsAnnotation(self):
        a = TsAnnotation()
        self.assertEqual(a.data, {})

    def test_load_annotation(self):
        a = TsAnnotation.load(self.annotation_path)
        self.assertEqual(a.data, self.annotation1)

    def test_validate_annotation(self):
        a = TsAnnotation.load(self.annotation_path)
        a.validate()

    def test_validation_error(self):
        a = TsAnnotation.load(self.annotation_error_path)
        try:
            a.validate()
            f = True
        except jsonschema.exceptions.ValidationError as e:
            f = False
        self.assertFalse(f)

    def test_equal_annotations(self):
        a1 = TsAnnotation.load(self.annotation_path)
        a2 = TsAnnotation.load(self.annotation_path)
        self.assertEqual(a1, a2)

    def test_crop(self):
        a = TsAnnotation(json_data={
            'annotations': [{'x': 24335.86, 'y': 1656.28, 'w': 6.28, 'h': 7.09, 'label': 'ship'},
                            {'x': 24754.72, 'y': 2877.79, 'w': 8.04, 'h': 7.12, 'label': 'ship'}]})

        ca1 = a.crop(0, 0, 100, 100)
        self.assertEqual(len(ca1), 0)
        ca2 = a.crop(24700, 2850, 25000, 2900)
        print(ca2)
        self.assertEqual(len(ca2), 1)
        print(a)
