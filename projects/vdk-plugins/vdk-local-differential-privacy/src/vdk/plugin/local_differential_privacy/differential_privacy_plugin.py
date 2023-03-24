# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging

from vdk.api.plugin.column_transformation_ingester_plugin import (
    ColumnTransformationIngestorPlugin,
)
from vdk.api.plugin.hook_markers import hookimpl
from vdk.api.plugin.plugin_input import IIngesterPlugin
from vdk.internal.builtin_plugins.run.job_context import JobContext
from vdk.internal.core.config import ConfigurationBuilder
from vdk.plugin.local_differential_privacy.differential_private_random_response import (
    DifferentialPrivateRandomResponse,
)
from vdk.plugin.local_differential_privacy.differential_private_unary_encoding import (
    DifferentialPrivateUnaryEncoding,
)
from vdk.plugin.local_differential_privacy.random_response_ingester_plugin import (
    RandomResponseIngesterPlugin,
)
from vdk.plugin.local_differential_privacy.unary_encoding_ingester_plugin import (
    UnaryEncodingIngesterPlugin,
)

IngestionMetadata = IIngesterPlugin.IngestionMetadata

log = logging.getLogger(__name__)


@hookimpl(tryfirst=True)
def vdk_configure(config_builder: ConfigurationBuilder) -> None:
    config_builder.add(
        key="differential_privacy_randomized_response_fields",
        default_value='{"table_name": ["column_name"]}',
        description="Map with entity/table name and list of attributes names that need to be privatized using random response."
        "The column must be of type boolean"
        "Checks are case sensitive.",
    )
    config_builder.add(
        key="differential_privacy_unary_encoding_fields",
        default_value='{"table_name": {"column_name": ["DOMAIN_VALUE_ONE", "DOMAIN_VALUE_TWO", "DOMAIN_VALUE_THREE"]}}',
        description="Map with entity/table name and list of attributes names that need to be privatized using unary encoding."
        "The property must be an enum like type with a finite set of values"
        "*The finite number of domain values must be known ahead of time and must never change when using unary encoding*"
        "Checks are case sensitive.",
    )


def get_json_for_prop(context: JobContext, prop: str) -> dict:
    return json.loads(context.core_context.configuration.get_value(prop) or "{}")


@hookimpl
def initialize_job(context: JobContext) -> None:
    context.ingester.add_ingester_factory_method(
        "random_response_differential_privacy",
        lambda: ColumnTransformationIngestorPlugin(
            RandomResponseIngesterPlugin(
                get_json_for_prop(
                    context, "differential_privacy_randomized_response_fields"
                ),
                DifferentialPrivateRandomResponse(2),
            )
        ),
    )

    context.ingester.add_ingester_factory_method(
        "unary_encoding_differential_privacy",
        lambda: ColumnTransformationIngestorPlugin(
            UnaryEncodingIngesterPlugin(
                get_json_for_prop(
                    context, "differential_privacy_unary_encoding_fields"
                ),
                DifferentialPrivateUnaryEncoding(0.75, 0.25),
            )
        ),
    )
