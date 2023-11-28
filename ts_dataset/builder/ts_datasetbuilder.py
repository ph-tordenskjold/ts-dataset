from dataset.ts_mtd import TsMTD


class TsDatasetBuilder:

    def __init__(self, name: str = "TsDataset", folder: str = ""):
        self._name = name
        self._mtd = TsMTD(json_data={})

    @property
    def name(self):
        return self._name

    def build(self):
        pass
