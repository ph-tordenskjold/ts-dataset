import os
import unittest

from tsdataset import settings, TsDatasetList, TsDataset
from tsdataset.meta import TsAnnotation


class TestDatasetList(unittest.TestCase):
    datasets_dir = settings.TEST_DATA
    d1_path = os.path.join(datasets_dir, 'test_dataset1')
    d2_path = os.path.join(datasets_dir, 'test_dataset2')
    error_path = os.path.join(datasets_dir, 'test_error_dataset')
    annotation_path1 = os.path.join(datasets_dir, 'test_dataset1', 'annotation1.json')
    annotation_path2 = os.path.join(datasets_dir, 'test_dataset1', 'test_folder_123', 'annotation2.json')

    def test_from_dir(self):
        ts = TsDatasetList(self.datasets_dir).load()
        self.assertEqual(len(ts.datasets), 2)
        self.assertEqual(len(ts), 4)

    def test_from_paths(self):
        ts = TsDatasetList([self.d1_path, self.d2_path])
        self.assertEqual(len(ts.datasets), 2)
        self.assertEqual(len(ts), 4)

    def test_from_dataset(self):
        ts = TsDatasetList(TsDataset(self.d1_path)).load()
        self.assertEqual(len(ts.datasets), 1)
        self.assertEqual(len(ts), 2)

    def test_from_datasets(self):
        ts = TsDatasetList([TsDataset(self.d1_path), TsDataset(self.d2_path)]).load()
        self.assertEqual(len(ts.datasets), 2)
        self.assertEqual(len(ts), 4)

    def test_getitem(self):
        ts = TsDatasetList(self.datasets_dir)
        a1 = TsAnnotation.load(self.annotation_path1)
        a2 = TsAnnotation.load(self.annotation_path2)

        self.assertEqual(ts[0], a1)
        self.assertEqual(ts[1], a1)
        self.assertEqual(ts[2], a2)
        self.assertEqual(ts[3], a2)
