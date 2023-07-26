# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import abc
import json
from enum import Enum
from enum import unique
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import click
from tabulate import tabulate


class Printer(abc.ABC):
    """
    The abstract base class for all printer classes.

    A printer is responsible for printing data in a specific format, such as text or JSON.
    Subclasses must implement the abstract methods below
    """

    @abc.abstractmethod
    def print_table(self, data: Optional[List[Dict[str, Any]]]) -> None:
        """
        Prints the table in the desired format  (text, json, etc)
        :param data: the table to print
        """

    @abc.abstractmethod
    def print_dict(self, data: Optional[Dict[str, Any]]) -> None:
        """
        Prints dictionary in the desired format  (text, json, etc)
        :param data: the dict to print
        """


"""
This dictionary contains all the registered printers.
The key is the output format and the value is the printer class.
Do not access this dictionary directly, use the printer decorator instead.
"""
_registered_printers = {}


def printer(output_format: str) -> callable:
    """
    A decorator that registers a printer class for the given output format.
    The class must implement the Printer interface and have a constructor with no parameters.

    :param output_format: The output format to register the printer for.
    """

    def decorator(cls):
        _registered_printers[output_format.lower()] = cls
        return cls

    return decorator


@printer("text")
class _PrinterText(Printer):
    def print_table(self, table: Optional[List[Dict[str, Any]]]) -> None:
        if table and len(table) > 0:
            click.echo(tabulate(table, headers="keys", tablefmt="fancy_grid"))
        else:
            click.echo("No Data.")

    def print_dict(self, data: Optional[Dict[str, Any]]) -> None:
        if data:
            click.echo(
                tabulate(
                    [[k, v] for k, v in data.items()],
                    headers=("key", "value"),
                )
            )
        else:
            click.echo("No Data.")


def json_format(data, indent=None):
    from datetime import date, datetime

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    return json.dumps(data, default=json_serial, indent=indent)


@printer("json")
class _PrinterJson(Printer):
    def print_table(self, data: List[Dict[str, Any]]) -> None:
        if data:
            click.echo(json_format(data))
        else:
            click.echo("[]")

    def print_dict(self, data: Dict[str, Any]) -> None:
        if data:
            click.echo(json_format(data))
        else:
            click.echo("{}")


def create_printer(output_format: str) -> Printer:
    """
    Creates a printer instance for the given output format.

    :param output_format: the desired output format
    :return: An instance of a Printer subclass that can print data in the desired format.

    """
    if output_format.lower() in _registered_printers:
        printer_class = _registered_printers[output_format.lower()]
        return printer_class()
    else:
        raise ValueError(f"Printer for output format {output_format} not registered")


@unique
class OutputFormat(str, Enum):
    """
    An enum used to specify the output formatting of a command.
    """

    TEXT = "TEXT"
    JSON = "JSON"
