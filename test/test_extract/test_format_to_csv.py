from util_functions import format_to_csv
import io
import csv
import pytest


class TestFormatToCsv:

    def test_returns_correct_type(self):
        rows = [["John", "Doe", 56], ["Jane", "Smith", 32]]
        columns = ["first_name", "last_name", "age"]
        buffer = format_to_csv(rows, columns)

        assert isinstance(buffer, io.StringIO) == True

    def test_returns_expected_format(self):
        rows = [["John", "Doe", "56"], ["Jane", "Smith", "32"]]
        columns = ["first_name", "last_name", "age"]
        buffer = format_to_csv(rows, columns)
        csv_reader = csv.reader(buffer)
        result_header = next(csv_reader)
        result_rows = list(csv_reader)

        assert result_header == columns
        assert result_rows == rows

    def test_returns_empty_list_if_no_rows_are_provided(self):
        rows = []
        columns = ["first_name", "last_name", "age"]
        buffer = format_to_csv(rows, columns)

        csv_reader = csv.reader(buffer)
        result_header = next(csv_reader)
        result_rows = list(csv_reader)

        assert result_header == columns
        assert result_rows == []

    def test_raises_exception_for_empty_columns(self):
        rows = [["John", "Doe", 56], ["Jane", "Smith", 32]]
        columns = []
        with pytest.raises(ValueError):
            format_to_csv(rows, columns)

    def test_pointer_position_is_reset_to_start(self):
        rows = [["John", "Doe", 56], ["Jane", "Smith", 32]]
        columns = ["first_name", "last_name", "age"]
        buffer = format_to_csv(rows, columns)

        assert buffer.tell() == 0
