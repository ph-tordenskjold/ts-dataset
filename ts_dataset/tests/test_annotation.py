import json
import os
import unittest

import jsonschema.exceptions

from ts_dataset import settings
from ts_dataset.meta import TsAnnotation


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
