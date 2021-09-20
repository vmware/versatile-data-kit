# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from typing import Dict

log = logging.getLogger(__name__)


class SqlArgumentSubstitutor:
    """
    Substitute text in provided SQL from provided dictory
    """

    def __init__(self, dictionary: Dict):
        self.dictionary = dictionary

    def substitute(self, sql: str) -> str:
        """Substitute text in provided SQL.

        e.g. a SQL like
        "SELECT {col1}, {col2} FROM {table}" and dictionary like {'col1': 'id', 'col2': 'pa__processed_ts', 'table': 'vm'}
        would result in the following SQL:
        "SELECT id, pa__processed_ts FROM vm"

        The substitution is case-sensitive.
        In case of variable that is used in the text, but not defined in the dictionary, there will be NO substitution
        and no error. For example:
        "SELECT {col1}, {col2} FROM {table}" and dictionary like {'col1': 'xxxxxx'} will result in
        "SELECT xxxxxx, {col2} FROM {table}"

        :return: String containing all the given text with substituted variables.
        """

        for key in self.dictionary:
            property_name = "{" + key + "}"
            if sql.find(property_name) != -1:
                property_value = str(self.dictionary[key])
                sql = sql.replace(property_name, property_value)
        return sql
