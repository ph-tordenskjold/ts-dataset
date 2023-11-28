import json
import os
import unittest

import jsonschema.exceptions

import settings
from dataset.ts_mtd import TsMTD


class TestMTD(unittest.TestCase):
    mtd_path = os.path.join(settings.BASE_DIR, 'test', 'data', 'test_dataset1', 'mtd.json')
    mtd_error_path = os.path.join(settings.BASE_DIR, 'test', 'data', 'mtd_error.json')

    def test_read_mtd(self):
        a = TsMTD.load(self.mtd_path)
        with open(self.mtd_path) as file:
            self.assertEqual(a.data, json.load(file))

    def test_eq(self):
        a1 = TsMTD.load(self.mtd_path)
        a2 = TsMTD.load(self.mtd_path)
        self.assertEqual(a1, a2)

    def test_not_eq(self):
        a1 = TsMTD.load(self.mtd_path)
        a2 = TsMTD()
        self.assertNotEqual(a1, a2)

    def test_validate(self):
        a = TsMTD.load(self.mtd_path).validate()

    def test_validate_error(self):
        try:
            a = TsMTD.load(self.mtd_error_path).validate()
            f = False
        except jsonschema.exceptions.ValidationError as e:
            f = True
        self.assertTrue(f)