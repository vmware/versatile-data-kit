# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
from collections import OrderedDict
from typing import List

import openai
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_registry import IPluginRegistry
from vdk.internal.builtin_plugins.connection.decoration_cursor import DecorationCursor
from vdk.internal.builtin_plugins.connection.execution_cursor import ExecutionCursor
from vdk.internal.core.config import ConfigurationBuilder
from vdk.internal.core.context import CoreContext

log = logging.getLogger(__name__)


class OpenAiPlugin:
    def __init__(self):
        self._review_enabled = False
        self._queries = OrderedDict()
        self._openai_model = "gpt-3.5-turbo"

    @hookimpl(tryfirst=True)
    def vdk_configure(self, config_builder: ConfigurationBuilder):
        # TODO: support non open ai models and make it configurable
        config_builder.add(
            key="openai_api_key",
            default_value="",
            description="""
                OpenAI API key. You can generete one on your OpenAI account page.
                (possibly https://platform.openai.com/account/api-keys)
                See best practices for api keys in https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety
            """,
        )
        config_builder.add(
            key="openai_model",
            default_value="text-davinci-003",
            description="""
                OpenAI model to be used.
                See more in https://platform.openai.com/docs/models/overview
            """,
        )
        config_builder.add(
            key="openai_review_enabled",
            default_value=False,
            description="If enabled, it will review each SQL query executed by the job and create summary file at the end.",
        )

    @hookimpl
    def vdk_initialize(self, context: CoreContext) -> None:
        openai.api_key = context.configuration.get_value("openai_api_key")
        self._review_enabled = context.configuration.get_value("openai_review_enabled")
        self._openai_model = context.configuration.get_value("openai_model")

    def _review_sql_query(self, sql_query: str):
        # Refine the prompt and make configurable
        # TODO provide SQL dialect to the prompt
        prompt = (
            """Using your extensive knowledge of SQL, analyze the following SQL query and provide a specific feedback.
        The feedback should include its efficiency, readability, possible optimization, potential errors,
        adherence to best practices, and security vulnerabilities, if any. Provide a score (1 a lot of work needed, 5 - no further changes needed)
         Return the answer in format {"score": ?, "review": "?" } Here is the SQL query:
        """
            + sql_query
        )

        # Generate the review
        # TODO: make configurable most things
        response = openai.Completion.create(
            engine=self._openai_model,
            prompt=prompt,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        # Extract the generated review from the response
        review = response.choices[0].text.strip()
        self._queries[sql_query] = review

        return review

    @hookimpl
    def db_connection_decorate_operation(
        self, decoration_cursor: DecorationCursor
    ) -> None:
        if self._review_enabled:
            try:
                managed_operation = decoration_cursor.get_managed_operation()
                review = self._review_sql_query(managed_operation.get_operation())
                log.info(
                    f"Query:\n{managed_operation.get_operation()}\n\nReview:\n{review}\n"
                )
            except Exception as e:
                log.error(f"Failed to review SQL query: {e}")

    @hookimpl
    def vdk_exit(self, context: CoreContext, exit_code: int) -> None:
        if self._review_enabled:
            with open("queries_reviews_report.md", "w") as f:
                f.write("# SQL Query Reviews\n")
                for query, review in self._queries.items():
                    f.write(f"## SQL Query\n\n```sql\n{query}\n```\n\n")
                    f.write(f"### Review\n\n{review}\n\n")


@hookimpl
def vdk_start(plugin_registry: IPluginRegistry, command_line_args: List):
    plugin_registry.load_plugin_with_hooks_impl(OpenAiPlugin(), "OpenAiPlugin")
