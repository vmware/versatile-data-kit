# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.api.job_input import IJobInput
from vdk.plugin.data_sources.factory import (
    SingletonDataSourceFactory,
)
from vdk.plugin.data_sources.ingester import DataSourceIngester
from vdk.plugin.singer.singer_data_source import SingerDataSourceConfiguration


def run(job_input: IJobInput):
    data_source = SingletonDataSourceFactory().create_data_source("singer-tap")
    config = SingerDataSourceConfiguration(
        tap_name="tap-gitlab",
        tap_config={
            "api_url": "https://gitlab.com/api/v4",
            "private_token": "",  # TODO
            "groups": "vmware-analytics",
            "projects": "vmware-analytics/versatile-data-kit",
            "start_date": "2018-01-01T00:00:00Z",
        },
        tap_auto_discover_schema=True,
    )

    data_source.configure(config)

    data_source_ingester = DataSourceIngester(job_input)

    data_source_ingester.ingest_data_source("gitlab", data_source, method="memory")

    data_source_ingester.terminate_and_wait_to_finish()
    data_source_ingester.raise_on_error()
