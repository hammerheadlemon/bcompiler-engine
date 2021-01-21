from dataclasses import dataclass
from typing import Dict, List, Tuple

from engine.config import Config


@dataclass
class ValidationCheck:
    passes: str
    filename: str
    key: str
    value: str
    cellref: str
    sheetname: str
    wanted: str
    got: str


class _ValidationState:
    def __init__(self, dm_line: Dict[str, str], sheet_data):
        self.new_state(_Unvalidated)
        self.sheet_data = sheet_data
        self.dm_line = dm_line
        self.cell_data = sheet_data[dm_line["cellref"]]
        self.validation_check = ValidationCheck(
            passes="",
            filename=self.cell_data["file_name"],
            key=self.dm_line["key"],
            value="",
            sheetname=self.dm_line["sheet"],
            cellref=self.dm_line["cellref"],
            wanted=self.dm_line["data_type"],
            got="",
        )

    def new_state(self, newstate):
        self.__class__ = newstate

    def check(self):
        raise NotImplementedError()

    def update_validation_check(self):
        raise NotImplementedError()


class _Unvalidated(_ValidationState):
    def check(self):
        if (
            self.dm_line["cellref"] in self.sheet_data.keys()
        ):
            # the fact there is a dml means we want a value
            self.new_state(_ValueWanted)
        else:
            self.new_state(_ValueUnwanted)


class _ValueWanted(_ValidationState):
    def check(self):
        if self.dm_line["data_type"] == "":
            self.new_state(_UnTyped)
        else:
            self.new_state(_Typed)


class _Typed(_ValidationState):
    def check(self):
        # Is the Type acceptable?
        if self.dm_line["data_type"] not in Config.ACCEPTABLE_VALIDATION_TYPES:
            self.validation_check.passes = "UNTYPED"
            self.new_state(_TypeNotMatched)
        elif self.dm_line["data_type"] == self.cell_data["data_type"]:
            self.validation_check.passes = "PASS"
            self.new_state(_TypeMatched)
        else:
            self.validation_check.passes = "FAIL"
            self.new_state(_TypeNotMatched)


class _UnTyped(_ValidationState):
    def check(self):
        self.validation_check.passes = "UNTYPED"
        self.validation_check.wanted = "NA"
        self.new_state(_TypeNotMatched)


class _TypeMatched(_ValidationState):
    def check(self):
        # the 'action' here is to update the got field and the passes field
        self.validation_check.got = self.cell_data["data_type"]
        self.validation_check.passes = "PASS"
        if self.cell_data["value"] == "":
            self.new_state(EmptyValue)
        else:
            self.new_state(_ValueGiven)


class _TypeNotMatched(_ValidationState):
    def check(self):
        # the 'action' here is to update the got field
        self.validation_check.got = self.cell_data["data_type"]
        if self.cell_data["value"] == "":
            self.new_state(EmptyValue)
        else:
            self.new_state(_ValueGiven)


class _EmptyValue(_ValidationState):
    def check(self):
        self.validation_check.value = "NO VALUE RETURNED"


class _ValueGiven(_ValidationState):
    def check(self):
        self.validation_check.value = self.cell_data["value"]
        self.new_state(_ValidationComplete)


class _ValueUnwanted(_ValidationState):
    def check(self):
        raise RuntimeError()


class _ValidationComplete(_ValidationState):
    def check(self):
        print("Validation Complete")


def _get_cellrefs(tmp_data, filename: str, sheet: str) -> List[str]:
    return tmp_data[filename]["data"][sheet].keys()


def _get_value(tmp_data, filename: str, sheet: str, cellref: str) -> str:
    return tmp_data[filename]["data"][sheet][cellref]["value"]


def _get_data_type(tmp_data, filename: str, sheet: str, cellref: str) -> str:
    return tmp_data[filename]["data"][sheet][cellref]["data_type"]


def validate_line(
    dml_data: Dict[str, str], sheet_data: Dict[str, Dict[str, str]]
) -> _ValidationState:
    """
    Given a Datamap line and sheet data, validate input.

    Returns a _ValidationState object containing a
    validation_check object containing results.
    """
    v = _ValidationState(dml_data, sheet_data)
    while True:
        v.check()
        if v.__class__ == _ValidationComplete:
            break
    return v


def validation_checker(dm_data, tmp_data) -> Tuple[List[str], List["ValidationCheck"]]:
    checks = []
    wrong_types = []
    files = tmp_data.keys()
    for d in dm_data:
        sheet = d["sheet"]
        vtype = d["data_type"]
        cellref = d["cellref"]
        for f in files:
            data = tmp_data[f]["data"]
            sheets = data.keys()
            for s in sheets:
                if s == sheet:
                    vout = validate_line(d, data[sheet])
                    checks.append(vout.validation_check)
    return (wrong_types, checks)
