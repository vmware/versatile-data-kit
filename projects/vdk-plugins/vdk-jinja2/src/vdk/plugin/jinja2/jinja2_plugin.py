# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from typing import cast

from jinja2 import BaseLoader
from jinja2 import Environment
from vdk.api.plugin.hook_markers import hookimpl
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.job_properties.properties_router import (
    PropertiesRouter,
)
from vdk.internal.builtin_plugins.run.job_context import JobContext


class Jinja2Plugin:
    def __init__(self):
        self.__job_input = None

    @hookimpl
    def run_job(self, context: JobContext) -> None:
        self.__job_input = context.job_input
        self.__properties_router = cast(PropertiesRouter, context.properties)

    def __get_substitute_variables(self):
        sql_susbstitute_args = {}
        if self.__properties_router.has_properties_impl():
            sql_susbstitute_args.update(self.__job_input.get_all_properties())
        sql_susbstitute_args.update(self.__job_input.get_execution_properties())
        sql_args = self.__job_input.get_arguments()
        if sql_args and type(sql_args) == dict:
            sql_susbstitute_args.update(sql_args)
        return sql_susbstitute_args

    @hookimpl(trylast=True)
    def db_connection_decorate_operation(self, decoration_cursor: DecorationCursor):
        managed_operation = decoration_cursor.get_managed_operation()

        statement = managed_operation.get_operation()
        environment = Environment(loader=BaseLoader)
        environment.globals.update(query=self.__job_input.execute_query)

        template = environment.from_string(statement)

        sql_susbstitute_args = self.__get_substitute_variables()
        statement = template.render(**sql_susbstitute_args)

        managed_operation.set_operation(statement)
