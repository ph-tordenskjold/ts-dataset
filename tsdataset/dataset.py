import json
import os
import typing

from tsdataset.meta import TsMTD, TsAnnotation


class TsDataset:

    def __init__(self, dataset_folder_path, validate: bool = True):
        self._data_folder_path = dataset_folder_path
        self._mtd_path = os.path.join(self._data_folder_path, 'mtd.json')
        self._mtd = None
        self._valid = False
        if validate:
            self.validate()

    def load(self):
        if not os.path.exists(self._mtd_path):
            raise FileNotFoundError(self._mtd_path)
        with open(self._mtd_path) as file:
            data = json.load(file)
            self._mtd = TsMTD(data)
        return self

    def validate(self):
        if not self.valid:
            self.load()
            self.mtd.validate()
            for annotation in self.mtd.data["annotations"]:
                TsAnnotation.load(os.path.join(self.dataset_folder_path, annotation)).validate()
            self._valid = True
        return self

    def __getitem__(self, index):
        return TsAnnotation.load(os.path.join(self.dataset_folder_path, self.mtd.data["annotations"][index]))

    @property
    def mtd(self) -> TsMTD:
        return self._mtd

    @property
    def valid(self) -> bool:
        return self._valid

    @property
    def mtd_path(self) -> str:
        return self._mtd_path

    @property
    def dataset_folder_path(self):
        return self._data_folder_path

    def __iter__(self):
        for annotation in self.mtd.data['annotations']:
            yield TsAnnotation.load(os.path.join(self.dataset_folder_path, annotation))

    def __len__(self):
        return len(self.mtd.data['annotations'])

    def add(self, other):
        dataset_list = TsDatasetList(self) + other
        return dataset_list

    def __add__(self, other):
        return self.add(other)


class TsDatasetList:
    def __init__(self, data_reference: typing.Union[str, typing.List[str], TsDataset, typing.List[TsDataset]]):
        """
            Parameters:
            - data_reference (Union[str, List[str], TsDataset, List[TsDataset]]):
                The input data reference, which can be one of the following:

                1. A directory path (str): The class will attempt to find all datasets in the specified directory
                   that conform to the time series (TS) dataset standard.

                2. A list of directory paths (List[str]): The class will create a TsDataset from each folder

                3. A TsDataset object (TsDataset): An instance of the TsDataset class.

                4. A list of TsDataset objects (List[TsDataset]): A list containing TsDataset objects.

            Note:
            - The class will use the provided data reference to initialize its internal state.
            - In the case of directory paths, the class will search for datasets conforming to the TS standard.
            - For TsDataset objects, they are directly used as input without further processing.

            Example:
            ```
            # Example 1: Initialize with a directory path
            obj = TsDatasetList("/path/to/dataset")

            # Example 2: Initialize with a list of directory paths
            obj = TsDatasetList(["/path/to/dataset1", "/path/to/dataset2"])

            # Example 3: Initialize with a TsDataset object
            ts_dataset = TsDataset(...)
            obj = TsDatasetList(ts_dataset)

            # Example 4: Initialize with a list of TsDataset objects
            ts_dataset_list = [TsDataset(...), TsDataset(...)]
            obj = TsDatasetList(ts_dataset_list)
            ```
            """
        self._datasets = []
        if isinstance(data_reference, str):
            assert os.path.exists(data_reference) and os.path.isdir(data_reference)
            for item in os.listdir(data_reference):
                try:
                    self._datasets.append(TsDataset(os.path.join(data_reference, item)))
                except Exception as e:  # TODO find a more specific error and maybe print error
                    pass
        elif isinstance(data_reference, list):
            if all(isinstance(item, str) for item in data_reference):
                self._datasets.extend([TsDataset(p) for p in data_reference])
            elif all(isinstance(item, TsDataset) for item in data_reference):
                self._datasets.extend(data_reference)
            else:
                raise TypeError("Invalid type in the list")
        elif isinstance(data_reference, TsDataset):
            self._datasets.append(data_reference)
        else:
            raise TypeError("Invalid type for data")

    def add(self, other: TsDataset):
        assert isinstance(TsDataset, other)
        if not other.valid:
            other.validate()
        self._datasets.append(other)

    def __add__(self, other: TsDataset):
        self.add(other)
        return self

    def __getitem__(self, index):
        for dataset in self.datasets:
            if index < len(dataset):
                return dataset[index]
            else:
                index -= len(dataset)

    def __len__(self):
        s = 0
        for dataset in self.datasets:
            s += len(dataset)
        return s

    def load(self):
        for dataset in self.datasets:
            dataset.load()
        return self

    @property
    def datasets(self) -> typing.List[TsDataset]:
        return self._datasets

    def validate(self):
        for dataset in self.datasets:
            dataset.validate()
        return self
