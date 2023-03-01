# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import ConfigurationBuilder

META_JOBS_DELAYED_JOBS_MIN_DELAY_SECONDS = "META_JOBS_DELAYED_JOBS_MIN_DELAY_SECONDS"
META_JOBS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS = (
    "META_JOBS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS"
)
META_JOBS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS = (
    "META_JOBS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS"
)
META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS = (
    "META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS"
)


class MetaPluginConfiguration:
    def __init__(self, config):
        self.__config = config

    def meta_jobs_delayed_jobs_min_delay_seconds(self):
        return self.__config.get_value(META_JOBS_DELAYED_JOBS_MIN_DELAY_SECONDS)

    def meta_jobs_delayed_jobs_randomized_added_delay_seconds(self):
        return self.__config.get_value(
            META_JOBS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS
        )

    def meta_jobs_dag_execution_check_time_period_seconds(self):
        return self.__config.get_value(
            META_JOBS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS
        )

    def meta_jobs_time_between_status_check_seconds(self):
        return self.__config.get_value(META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS)


def add_definitions(config_builder: ConfigurationBuilder):
    config_builder.add(
        key=META_JOBS_DELAYED_JOBS_MIN_DELAY_SECONDS,
        default_value=30,
        description="TODO",
    )
    config_builder.add(
        key=META_JOBS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS,
        default_value=600,
        description="TODO",
    )
    config_builder.add(
        key=META_JOBS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS,
        default_value=10,
        description="TODO",
    )
    config_builder.add(
        key=META_JOBS_TIME_BETWEEN_STATUS_CHECK_SECONDS,
        default_value=40,
        description="TODO",
    )
