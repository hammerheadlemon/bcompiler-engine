import json
import os
from pathlib import Path
from typing import List, Tuple

from openpyxl import Workbook, load_workbook

from engine.use_cases.parsing import \
    extract_from_multiple_xlsx_files as extract
from engine.use_cases.typing import MASTER_COL_DATA, MASTER_DATA_FOR_FILE
from engine.utils.extraction import ALL_IMPORT_DATA, _get_xlsx_files

from ..config import Config


class MultipleTemplatesWriteRepo:
    """Write data to a blank template.

    Given data (e.g. from extracted from a master xlsx file), writes
    each data set to a blank template and save it in the output directory,
    which by default is in "User/Documents/bcompiler/output."
    """

    def __init__(self, blank_template: Path):
        "directory_path is the directory in which to write the files."
        self.output_path = Config.PLATFORM_DOCS_DIR / "output"
        self.blank_template = blank_template
        self.unsaved_workbooks: List[Tuple[str, Workbook]] = []

    def _populate_workbook(
        self, workbook: Workbook, file_data: MASTER_COL_DATA
    ) -> Workbook:
        for cell in file_data:
            _sheet = workbook.get_sheet_by_name(cell.sheet)
            try:
                _sheet[cell.cellref].value = cell.value
            except AttributeError:
                # TODO fix the wording for this exception
                raise AttributeError(
                    "PROBLEM: Object->{} Current Val->{} Attempted Val->{}".format(
                        cell, cell.value, _sheet[cell.cellref].value
                    )
                )
        return workbook

    def write(self, data: MASTER_DATA_FOR_FILE, from_json: bool = False) -> None:
        """Writes data from a single column in a master Excel file to a file.

        data: list of ColData tuples, which contains the key, sheet and value
        file_name: file name to be appended to output path
        """
        blank_workbook: Workbook = load_workbook(
            self.blank_template, read_only=False, keep_vba=True
        )
        for file_data in data:
            file_name = file_data[0].file_name
            _wb = self._populate_workbook(blank_workbook, file_data)
            output_file_name: str = ".".join([file_name, "xlsm"])
            self.unsaved_workbooks.append((output_file_name, _wb))
        self._write_each_workbook()


    def _save_workbook(self, wb_t: Tuple[str, Workbook]) -> None:
        _wb = wb_t[1]
        _output_file_name = wb_t[0]
        print("Saving {}".format(_output_file_name))
        _wb.save(filename=Config.PLATFORM_DOCS_DIR / "output" / _output_file_name)


    def _write_each_workbook(self) -> None:
        for wb in map(self._save_workbook, self.unsaved_workbooks):
            pass


class FSPopulatedTemplatesRepo:
    "A repo that is based on a single data file in the .bcompiler-engine directory."

    def __init__(self, directory_path: str):
        self.directory_path = directory_path

    def list_as_json(self) -> str:
        "Try to open the data file containing populated data as json."
        try:
            with open(
                os.path.join(Config.BCOMPILER_LIBRARY_DATA_DIR, "extracted_data.dat")
            ) as data_file:
                return data_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find file.")


class InMemoryPopulatedTemplatesRepository:
    "A repo that does no data file reading or writing - just parsing from excel files."

    def __init__(self, directory_path: str) -> None:
        self.directory_path = directory_path
        self.state: ALL_IMPORT_DATA = {}

    def list_as_json(self) -> str:
        "Return data from a directory of populated templates as json."
        excel_files = _get_xlsx_files(self.directory_path)
        if not self.state:
            self.state = extract(excel_files)
            return json.dumps(self.state)
        else:
            return json.dumps(self.state)
