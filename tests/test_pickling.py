import hashlib

import pytest

from engine.parser import (
    get_xlsx_files,
    hash_target_files,
    parse_multiple_xlsx_files,
    template_reader,
    hash_single_file,
)


def test_hash_of_single_file(resources):
    hash_obj = hashlib.md5(open(resources / "test_template.xlsx", "rb").read())
    assert hash_obj.digest() == hash_single_file(resources / "test_template.xlsx")


def test_hash_of_target_files(resources):
    test_file_name = "test_template.xlsx"
    excel_files = get_xlsx_files(resources)
    test_file = [x for x in excel_files if x.name == test_file_name][0]
    digest_of_test_file = hashlib.md5(open(test_file, "rb").read()).digest()
    get_hashes = hash_target_files(excel_files)
    computed_hash = get_hashes[test_file_name]
    assert digest_of_test_file == computed_hash


def test_group_data_by_source_file(resources):
    test_file_name = "test_template.xlsx"
    excel_files = get_xlsx_files(resources)
    test_file = [x for x in excel_files if x.name == test_file_name][0]
    digest_of_test_file = hashlib.md5(open(test_file, "rb").read()).digest()
    dataset = parse_multiple_xlsx_files(excel_files)
    assert dataset["test_template.xlsx"]["checksum"] == digest_of_test_file


@pytest.mark.skip("Not ready for this yet")
def test_pickle_data_from_multiple_files(resources):
    xlsx_files = get_xlsx_files(resources)
    dataset = parse_multiple_xlsx_files(xlsx_files)
    file_hashes = hash_target_files(xlsx_files)