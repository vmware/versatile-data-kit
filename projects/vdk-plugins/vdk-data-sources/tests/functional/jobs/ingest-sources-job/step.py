# Copyright 2023-2024 Broadcom
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.auto_generated import (
    AutoGeneratedDataSourceConfiguration,
)
from vdk.plugin.data_sources.factory import (
    SingletonDataSourceFactory,
)
from vdk.plugin.data_sources.ingester import DataSourceIngester


def run(job_input: IJobInput):
    # TODO: this is not the expected user experience
    # this would be changed as the interface matures.

    auto_generated = SingletonDataSourceFactory().create_data_source(
        "auto-generated-data"
    )
    auto_generated.configure(AutoGeneratedDataSourceConfiguration())

    data_source_ingester = DataSourceIngester(job_input)

    data_source_ingester.ingest_data_source("auto", auto_generated, method="memory")

    data_source_ingester.terminate_and_wait_to_finish()
    data_source_ingester.raise_on_error()
