from dataset.ts_json import TsJson


class TsAnnotation(TsJson):

    def __init__(self, json_data: dict = None):
        super().__init__(json_data)
        self._schema = 'annotation_schema.json'
