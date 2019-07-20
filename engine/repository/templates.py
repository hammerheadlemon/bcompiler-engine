import json
import os
from typing import TYPE_CHECKING, Any, Dict, Iterator

from engine.use_cases.parsing import \
    extract_from_multiple_xlsx_files as extract
from engine.utils.extraction import _get_xlsx_files

from ..config import Config

if TYPE_CHECKING:
    from engine.use_cases.parsing import DatamapFile


class FSPopulatedTemplatesRepo:
    "A repo that is based on a single data file in the .bcompiler-engine directory."

    def __init__(self, directory_path: str, datamap: "DatamapFile" = None) -> None:
        self.directory_path = directory_path

    def return_iterator(self, filename: str, sheetname: str) -> Iterator[Dict[str, Any]]:
        pass

    def apply_datamap(self, datamap: "DatamapFile" = None) -> str:
        "Use a datamap to filter the output from data extracted from a repo."
        try:
            return self.list_as_json()
        except FileNotFoundError:
            excel_files = _get_xlsx_files(self.directory_path)
            data = extract(excel_files)
            return data

    def list_as_json(self) -> str:
        "Try to open the data file containing populated data as json."
        try:
            with open(
                    os.path.join(Config.BCOMPILER_LIBRARY_DATA_DIR,
                                 "extracted_data.dat")) as data_file:
                return data_file.read()
        except FileNotFoundError:
            raise FileNotFoundError("Cannot find file.")


class InMemoryPopulatedTemplatesRepository:
    "A repo that does no data file reading or writing - just parsing from excel files."

    def __init__(self, directory_path: str, datamap: "DatamapFile" = None) -> None:
        self.directory_path = directory_path

    def list_as_json(self) -> str:
        "Return data from a directory of populated templates as json."
        excel_files = _get_xlsx_files(self.directory_path)
        data = extract(excel_files)
        return json.dumps(data)
