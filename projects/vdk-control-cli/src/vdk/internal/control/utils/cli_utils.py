# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import functools
import json
import logging
import os
import shutil
from dataclasses import dataclass
from enum import Enum
from enum import unique

import click
from vdk.internal.control.configuration.defaults_config import load_default_rest_api_url
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.control.exception.vdk_exception import VDKException


log = logging.getLogger(__name__)


def get_or_prompt(option_description, option_value, default_value=None):
    if not option_value:
        option_value = click.prompt(option_description, default=default_value)
    return option_value


def extended_option(hide_if_default=False):
    """Extends click option with extra functionality:
    * Records default value if coming from default_map in help (click does not)
    * Flag to hide options with default value (so that administrative option can be hidden)
    """

    class OptionExtended(click.Option):
        def get_help_record(self, ctx):
            self.show_default = True
            default_value = ctx.lookup_default(self.name)
            if default_value is not None:
                if hide_if_default:
                    self.hidden = True
                self.default = default_value
            return super().get_help_record(ctx)

    return OptionExtended


def rest_api_url_option(*names, **kwargs):
    """
    A decorator that adds a `--rest-api-url, -u` option to the decorated
    command.
    Name can be configured through ``*names``. Keyword arguments are passed to
    the underlying ``click.option`` decorator.
    """
    if not names:
        names = ["--rest-api-url", "-u"]

    def decorator(f):
        return click.option(
            *names,
            type=click.STRING,
            cls=extended_option(hide_if_default=True),
            help="The base REST API URL. It looks like http://server (without path e.g. /data-jobs)",
            default=VDKConfig().control_service_rest_api_url
            or load_default_rest_api_url(),
            **kwargs,
        )(f)

    return decorator


def check_rest_api_url(rest_api_url: str):
    if not rest_api_url:
        raise VDKException(
            what="Cannot connect to the Control Service.",
            why="The following (mandatory) option is missing (--rest-api-url). Please, provide a valid value.",
            consequence="Cannot manage (create, execute, delete, etc.) data jobs.",
            countermeasure="Verify that the --rest-api-url is specified, either directly or via a plugin.",
        )


def check_required_parameters(f):
    """
    A decorator that checks whether the `--rest-api-irl` parameter is specified
    before calling the wrapped function and, if not, throws an exception.
    """

    @functools.wraps(f)
    def check(*args, **kwargs):
        log.debug(f"Passed parameters to function {f}: {args}, {kwargs}")
        rest_api_url = kwargs.get("rest_api_url", "")
        check_rest_api_url(rest_api_url)

        return f(*args, **kwargs)

    return check


@unique
class OutputFormat(str, Enum):
    """
    An enum used to specify the output formatting of a command.
    """

    TEXT = "TEXT"
    JSON = "JSON"


def output_option(*names, **kwargs):
    """
    A decorator that adds an `--output, -o` option to the decorated command.
    Name can be configured through ``*names``. Keyword arguments are passed to
    the underlying ``click.option`` decorator.
    """
    if not names:
        names = ["--output", "-o"]

    def decorator(f):
        return click.option(
            *names,
            type=click.Choice([e.value for e in OutputFormat], case_sensitive=False),
            default=OutputFormat.TEXT.value,
            cls=extended_option(hide_if_default=True),
            help="The desirable format of the result. Supported formats include text and json.",
            **kwargs,
        )(f)

    return decorator


def json_format(data, indent=None):
    from datetime import date, datetime

    def json_serial(obj):
        """JSON serializer for objects not serializable by default json code"""

        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError("Type %s not serializable" % type(obj))

    return json.dumps(data, default=json_serial, indent=indent)


def copy_directory(src, dst):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        source_file = os.path.join(src, item)
        dest_file = os.path.join(dst, item)
        if os.path.isfile(source_file):
            shutil.copy(source_file, dest_file)


@dataclass
class QueryField:
    name: str = ""
    alias: str = ""
    arguments: dict[str, str | int] = None
    fields: list[QueryField] = None

    def __hash__(self):
        return self.name.__hash__()

    def __eq__(self, other):
        return self.name.__eq__(other)

    def to_string(self):
        field_as_string = self.name
        if self.arguments:
            arguments_as_strings: list[str] = []
            for key, value in self.arguments.items():
                arguments_as_strings.append(f"{key}: {value}")
            field_as_string = (
                field_as_string + "(" + ", ".join(arguments_as_strings) + ")"
            )
        if self.alias:
            field_as_string = f"{self.alias}: {field_as_string}"
        if self.fields:
            field_as_string = (
                field_as_string + " { " + " ".join(map(str, self.fields)) + " } "
            )
        return field_as_string

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()

    def add(self, name: str, alias: str = None, arguments: dict[str, str | int] = None):
        """
        Add new field as child to the current field and return current field
        So you can chain multiple children of one field
        Example:
        root_field.add('child1').add(child2)

        :param name: the name of the field
        :param alias: alias name for the field if applicable , by default emptyh
        :param arguments: arguments to pass to the field, including any filters
        :return: the current field
        """
        self.add_return_new(name, alias, arguments)
        return self

    def add_return_new(
        self, name: str, alias: str = None, arguments: dict[str, str | int] = None
    ):
        """
        Add new field as child to the current field and return newly added field
        Example:
        root_field.add_return_new('child').add_return_new('grand_child')

        :param name: the name of the field
        :param alias: alias name for the field if applicable, by default empty
        :param arguments: arguments to pass to the field, including any filters
        :return: the newly created field.
        """
        query_field = QueryField(name=name, alias=alias, arguments=arguments)
        if not self.fields:
            self.fields = []
        self.fields.append(query_field)
        return query_field


@dataclass
class GqlQueryBuilder:
    """
    Help Builds GraphQL query.
    For our simple cases we do not need anything more complicated like https://pypi.org/project/gql
    It covers only basic querying of fields
    """

    def __init__(self):
        self.__root_field = QueryField("jobs")

    def start(self) -> QueryField:
        """
        Start new build process. It will reset current progress
        """
        self.__root_field = QueryField("")
        return self.__root_field

    def build(self) -> str:
        """
        Return GraphQL like query to list all added fields
        """
        return str(self.__root_field).strip()
