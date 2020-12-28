# engine.reports.validation.py
#
# Write a validation report to a CSV file.

import csv
import datetime
from dataclasses import dataclass
from typing import List

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


class ValidationReportCSV:
    """
    Writes a CSV output for validation_data at
    Config.FULL_PATH_OUTPUT/validation_report.csv
    """

    def __init__(self, validation_data: List[ValidationCheck]):
        self.data = validation_data

    def write(self) -> None:
        timestamp = (
            datetime.datetime.today()
            .isoformat(timespec="seconds")
            .replace(":", "_")
            .replace("-", "_")
        )
        with open(
            Config.FULL_PATH_OUTPUT / f"validation_report_{timestamp}.csv",
            "w",
            newline="",
        ) as csvfile:
            fieldnames = [
                "Pass Status",
                "Filename",
                "Key",
                "Value",
                "Cell Reference",
                "Sheet Name",
                "Expected Type",
                "Got Type",
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for item in self.data:
                # TODO - REPLACE with better cleaning function
                # This prevented values with ; in them spreading the
                # text across multiple cells in the CSV output
                try:
                    item.value = item.value.replace(";", "")
                except AttributeError:
                    pass
                writer.writerow(
                    {
                        "Pass Status": item.passes,
                        "Filename": item.filename,
                        "Key": item.key,
                        "Value": item.value,
                        "Cell Reference": item.cellref,
                        "Sheet Name": item.sheetname,
                        "Expected Type": item.wanted,
                        "Got Type": item.got,
                    }
                )
