from dataset.ts_json import TsJson


class TsMTD(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data=json_data)
        self._schema = 'mtd_schema.json'
