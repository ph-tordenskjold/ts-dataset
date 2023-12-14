import json
import os
import unittest

from tsdataset import settings, TsDataset
from tsdataset.meta import TsAnnotation


class TestDataset(unittest.TestCase):
    dataset_path = os.path.join(settings.TEST_DATA, 'test_dataset1')
    error_path = os.path.join(settings.TEST_DATA, 'test_error_dataset')
    annotation_path1 = os.path.join(settings.TEST_DATA, 'test_dataset1', 'annotation1.json')
    annotation_path2 = os.path.join(settings.TEST_DATA, 'test_dataset1', 'test_folder_123',
                                    'annotation2.json')

    def test_find_mtd(self):
        a = TsDataset(dataset_folder_path=self.dataset_path)
        self.assertEqual(a.mtd_path, os.path.join(self.dataset_path, 'mtd.json'))

    def test_load_finds_both_annotations(self):
        a = TsDataset(dataset_folder_path=self.dataset_path).load()
        self.assertEqual(len(a.mtd.data["annotations"]), 2)

    def test_validate_schema(self):
        a = TsDataset(dataset_folder_path=self.dataset_path).load().validate()

    def test_error_folder(self):
        try:
            a = TsDataset(dataset_folder_path=self.error_path).load()
            f = False
        except FileNotFoundError as e:
            f = True
        self.assertTrue(f)

    def test_iter(self):
        with open(self.annotation_path1) as f1:
            with open(self.annotation_path2) as f2:
                a1 = json.load(f1)
                a2 = json.load(f2)
        a = TsDataset(dataset_folder_path=self.dataset_path).load()
        for i in a:
            self.assertTrue(TsAnnotation(a1) == i or TsAnnotation(a2) == i)

    def test_getitem(self):
        with open(self.annotation_path1) as f1:
            with open(self.annotation_path2) as f2:
                a1 = json.load(f1)
                a2 = json.load(f2)
        a = TsDataset(dataset_folder_path=self.dataset_path).load()
        self.assertTrue(TsAnnotation(a1) == a[0])
        self.assertTrue(TsAnnotation(a2) == a[1])
