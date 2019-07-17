import json
from typing import Dict


class TemplateCellSerializer(json.JSONEncoder):
    def default(self, o) -> Dict[str, str]:
        try:
            to_serialize = {
                "file_name": o.file_name,
                "sheet_name": o.sheet_name,
                "cellref": o.cellref,
                "data_type": o.data_type.name,
            }
            return to_serialize
        except AttributeError:
            return super().default(o)
