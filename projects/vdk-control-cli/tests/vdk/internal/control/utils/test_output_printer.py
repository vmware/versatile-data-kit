# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import unittest
from typing import Any
from typing import Dict
from typing import List
from unittest.mock import patch

import pytest
from vdk.internal.control.utils import output_printer
from vdk.internal.control.utils.output_printer import create_printer
from vdk.internal.control.utils.output_printer import InMemoryTextPrinter
from vdk.internal.control.utils.output_printer import Printer
from vdk.internal.control.utils.output_printer import PrinterJson
from vdk.internal.control.utils.output_printer import PrinterText


class TestPrinterText:
    def test_print_dict(self):
        with patch("click.echo") as mock_echo:
            printer = PrinterText()
            data = {"key": "value"}

            printer.print_dict(data)

            expected_output = "key    value\n" "-----  -------\n" "key    value"
            mock_echo.assert_called_once_with(expected_output)

    def test_print_table_with_data(self):
        with patch("click.echo") as mock_echo:
            printer = PrinterText()

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
            printer = PrinterText()
            data = []

            printer.print_table(data)

            expected_output = "No Data."
            mock_echo.assert_called_once_with(expected_output)


class TestPrinterJson:
    def test_print_dict(self):
        with patch("click.echo") as mock_echo:
            printer = PrinterJson()

            data = {"key": "value"}

            printer.print_dict(data)

            expected_output = '{"key": "value"}'
            mock_echo.assert_called_once_with(expected_output)

    def test_print_table(self):
        with patch("click.echo") as mock_echo:
            printer = PrinterJson()
            data = [
                {"key1": "value1", "key2": "value2"},
                {"key1": "value3", "key2": "value4"},
            ]
            printer.print_table(data)

            expected_output = '[{"key1": "value1", "key2": "value2"}, {"key1": "value3", "key2": "value4"}]'
            mock_echo.assert_called_once_with(expected_output)


class TestMemoryPrinter(unittest.TestCase):
    def setUp(self):
        self.printer = InMemoryTextPrinter()

    def test_print_dict(self):
        data = {"key": "value"}

        self.printer.print_dict(data)

        output = self.printer.output_buffer.getvalue().strip()

        self.assertIn("key", output)
        self.assertIn("value", output)

    def test_print_table(self):
        data = [
            {"key1": "value1", "key2": "value2"},
            {"key1": "value3", "key2": "value4"},
        ]
        self.printer.print_table(data)

        output = self.printer.output_buffer.getvalue().strip()

        self.assertIn("key1", output)
        self.assertIn("key2", output)
        self.assertIn("value1", output)
        self.assertIn("value2", output)
        self.assertIn("value3", output)
        self.assertIn("value4", output)

    def test_print_dict_no_data(self):
        self.printer.cleanup()
        self.printer.print_dict(None)

        expected_output = "No Data."
        actual_output = self.printer.output_buffer.getvalue().strip()

        self.assertEqual(actual_output, expected_output)

    def test_print_table_no_data(self):
        self.printer.cleanup()
        self.printer.print_table(None)

        expected_output = "No Data."
        actual_output = self.printer.output_buffer.getvalue().strip()

        self.assertEqual(actual_output, expected_output)

    def test_cleanup(self):
        data = {"key": "value"}
        self.printer.print_dict(data)
        self.printer.cleanup()
        actual_output = self.printer.output_buffer.getvalue()
        self.assertEqual(actual_output, "")


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
