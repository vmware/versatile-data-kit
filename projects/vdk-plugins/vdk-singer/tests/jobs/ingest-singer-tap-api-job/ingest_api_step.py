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
        tap_name="tap-rest-api-msdk",
        tap_config={
            "api_url": job_input.get_arguments().get("api_url"),
            "streams": [
                {
                    "name": "some_data",
                    "path": "/fake_data",
                    "records_path": "$.[*]",
                    "num_inference_records": 200,
                },
                {
                    "name": "some_nested_data",
                    "path": "/nested_fake_data",
                    "records_path": "$.[*]",
                    "num_inference_records": 200,
                },
            ],
        },
        tap_auto_discover_schema=True,
    )

    data_source.configure(config)

    data_source_ingester = DataSourceIngester(job_input)

    data_source_ingester.ingest_data_source(
        "fake-api",
        data_source,
        method=job_input.get_arguments().get("method", "sqlite"),
    )

    data_source_ingester.terminate_and_wait_to_finish()
    data_source_ingester.raise_on_error()
