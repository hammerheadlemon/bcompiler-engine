import json

from engine.domain.datamap import DatamapLine
from engine.serializers.datamap import datamap_json_serializer


def test_datamapline_obj_to_dict():
    dml1 = DatamapLine(
        key="Test 1",
        sheet="Summary",
        cellref="A10",
        data_type="TEXT",
        filename="test.csv",
    )
    assert dml1.to_dict()["key"] == "Test 1"


def test_datamap_json_serializer():
    dml1 = DatamapLine(
        key="Test 1",
        sheet="Summary",
        cellref="A10",
        data_type="TEXT",
        filename="test.csv",
    )
    lst = [dml1]
    expected_json = """
        [{"key": "Test 1", "sheet": "Summary", "cellref": "A10", "data_type": "TEXT", "filename": "test.csv"}]
    """
    datamap_in_json = json.loads(datamap_json_serializer(lst))
    assert datamap_in_json == json.loads(expected_json)
