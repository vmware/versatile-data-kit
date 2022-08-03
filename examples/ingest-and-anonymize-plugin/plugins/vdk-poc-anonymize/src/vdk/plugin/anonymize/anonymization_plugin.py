# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging

from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.anonymize.anonymizer import Anonymizer
from vdk.plugin.anonymize.ingester_plugin import AnonymizationIngesterPlugin

IngestionMetadata = IIngesterPlugin.IngestionMetadata

log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    # Declare needed configuration, it will be injected automatically fron file, env variables, etc.
    config_builder.add(
        key="anonymization_fields",
        default_value='{"table_name": ["column_name"]}',
        description="Map with entity/table name and list of attributes names that need to be anonymized."
        "Checks are case sensitive.",
    )


@hookimpl
def initialize_job(context: JobContext) -> None:
    # Now let's get the correctly configured value
    anonymization_fields = context.core_context.configuration.get_value(
        "anonymization_fields"
    )
    anonymization_fields = json.loads(anonymization_fields)
    context.ingester.add_ingester_factory_method(
        "anonymize",
        lambda: AnonymizationIngesterPlugin(anonymization_fields, Anonymizer()),
    )
