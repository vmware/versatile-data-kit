# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest
from vdk.internal.control.utils import output_printer
from vdk.internal.control.utils.output_printer import _PrinterJson
from vdk.internal.control.utils.output_printer import _PrinterText
from vdk.internal.control.utils.output_printer import create_printer
from vdk.internal.control.utils.output_printer import Printer


class TestPrinterText:
    def test_print_dict(self):
        with patch("click.echo") as mock_echo:
            printer = _PrinterText()
            data = {"key": "value"}

            printer.print_dict(data)

            expected_output = "key    value\n" "-----  -------\n" "key    value"
            mock_echo.assert_called_once_with(expected_output)

    def test_print_table_with_data(self):
        with patch("click.echo") as mock_echo:
            printer = _PrinterText()

            data = [{"key1": "value1", "key2": 2}, {"key1": "value3", "key2": 4}]

            printer.print_table(data)

            expected_output = (
                "╒════════╤════════╕\n"
                "│ key1   │   key2 │\n"
                "╞════════╪════════╡\n"
                "│ value1 │      2 │\n"
                "├────────┼────────┤\n"
                "│ value3 │      4 │\n"
                "╘════════╧════════╛"
            )
            mock_echo.assert_called_once_with(expected_output)

    def test_print_table_with_no_data(self):
        with patch("click.echo") as mock_echo:
            printer = _PrinterText()
            data = []

            printer.print_table(data)

            expected_output = "No Data."
            mock_echo.assert_called_once_with(expected_output)


class TestPrinterJson:
    def test_print_dict(self):
        with patch("click.echo") as mock_echo:
            printer = _PrinterJson()

            data = {"key": "value"}

            printer.print_dict(data)

            expected_output = '{"key": "value"}'
            mock_echo.assert_called_once_with(expected_output)

    def test_print_table(self):
        with patch("click.echo") as mock_echo:
            printer = _PrinterJson()
            data = [
                {"key1": "value1", "key2": "value2"},
                {"key1": "value3", "key2": "value4"},
            ]
            printer.print_table(data)

            expected_output = '[{"key1": "value1", "key2": "value2"}, {"key1": "value3", "key2": "value4"}]'
            mock_echo.assert_called_once_with(expected_output)


class TestCreatePrinter:
    def test_create_printer_with_registered_format(self):
        class MockPrinter(Printer):
            def print_dict(self, data: Dict[str, Any]) -> None:
                pass

            def print_table(self, data: List[Dict[str, Any]]) -> None:
                pass

        output_printer._registered_printers["mock"] = MockPrinter

        printer = create_printer("mock")
        assert isinstance(printer, MockPrinter)

    def test_create_printer_with_unregistered_format(self):
        with pytest.raises(ValueError):
            create_printer("invalid_format")
