import json


class TemplateCellSerializer(json.JSONEncoder):
    def default(self, o):
        try:
            to_serialize = {
                "file_name": o.file_name,
                "sheet_name": o.sheet_name,
                "cellref": o.cellref,
            }
            return to_serialize
        except AttributeError:
            return super().default(o)  # type: ignore
