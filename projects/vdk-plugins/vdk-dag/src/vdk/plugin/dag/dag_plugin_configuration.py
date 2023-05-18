# Copyright 2023-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
from vdk.internal.core.config import Configuration
from vdk.internal.core.config import ConfigurationBuilder

DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS = "DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS"
DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS = (
    "DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS"
)
DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS = (
    "DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS"
)
DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS = "DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS"
DAGS_MAX_CONCURRENT_RUNNING_JOBS = "DAGS_MAX_CONCURRENT_RUNNING_JOBS"


class DagPluginConfiguration:
    def __init__(self, config: Configuration):
        self.__config = config

    def dags_delayed_jobs_min_delay_seconds(self):
        """
        Returns the minimum delay time for a delayed job to be executed in seconds.

        :return: the number of seconds for the minimum delay of a delayed job

        :seealso: `DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS <https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-dag/src/vdk/plugin/dag/dag_plugin_configuration.py#L90>`
        """
        return self.__config.get_value(DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS)

    def dags_delayed_jobs_randomized_added_delay_seconds(self):
        """
        Returns the additional randomized delay time in seconds to the minimum delay time of a delayed job.

        :return: the number of seconds for the additional randomized delay of the delayed jobs

        :seealso: `DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS <https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-dag/src/vdk/plugin/dag/dag_plugin_configuration.py#L100>`
        """
        return self.__config.get_value(DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS)

    def dags_dag_execution_check_time_period_seconds(self):
        """
        Returns the frequency at which the system checks a DAG execution's status.

        :return: the frequency in seconds at which the system checks a DAG execution's status

        :seealso: `DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS <https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-dag/src/vdk/plugin/dag/dag_plugin_configuration.py#L111>`
        """
        return self.__config.get_value(DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS)

    def dags_time_between_status_check_seconds(self):
        """
        Returns the time interval in seconds between status checks for a job.

        :return: the number of seconds between status checks for a job.

        :seealso: `DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS <https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-dag/src/vdk/plugin/dag/dag_plugin_configuration.py#L121>`
        """
        return self.__config.get_value(DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS)

    def dags_max_concurrent_running_jobs(self):
        """
        Returns the limit of concurrent running jobs.

        :return: the number of maximum concurrent running jobs

        :seealso: `DAGS_MAX_CONCURRENT_RUNNING_JOBS <https://github.com/vmware/versatile-data-kit/blob/main/projects/vdk-plugins/vdk-dag/src/vdk/plugin/dag/dag_plugin_configuration.py#L132>`
        """
        return self.__config.get_value(DAGS_MAX_CONCURRENT_RUNNING_JOBS)


def add_definitions(config_builder: ConfigurationBuilder):
    """
    Defines what configuration settings are needed for the DAGs plugin with reasonable defaults.

    :param config_builder: the builder used to add the configuration variables
    :return:
    """
    config_builder.add(
        key=DAGS_DELAYED_JOBS_MIN_DELAY_SECONDS,
        default_value=30,
        description=(
            "This sets the minimum delay time for a delayed job to be executed. "
            "Delayed jobs are not scheduled to run immediately due to issues such as "
            "server errors or concurrent job limits. For instance, a delay time of 30 "
            "seconds would mean the system waits at least 30 seconds before retrying the job."
        ),
    )
    config_builder.add(
        key=DAGS_DELAYED_JOBS_RANDOMIZED_ADDED_DELAY_SECONDS,
        default_value=600,
        description=(
            "This sets an additional randomized delay time in seconds to the minimum delay time "
            "of a delayed job. For instance, setting this option to 10 seconds would mean the "
            "system adds a random delay of up to 10 seconds before retrying the job. "
            "The randomized delay helps to spread out job execution over a longer period and "
            "prevent resource contention issues."
        ),
    )
    config_builder.add(
        key=DAGS_DAG_EXECUTION_CHECK_TIME_PERIOD_SECONDS,
        default_value=10,
        description=(
            "This sets the frequency at which the system checks a DAG execution's status to see "
            "if any running jobs have completed and if new jobs need to start. For instance, setting "
            "this option to 10 seconds would mean the system checks the DAG status every 10 seconds "
            "to ensure successful job execution. It's advisable to use the default value for this variable."
        ),
    )
    config_builder.add(
        key=DAGS_TIME_BETWEEN_STATUS_CHECK_SECONDS,
        default_value=40,
        description=(
            "This sets the time interval in seconds between status checks for a job. The system periodically "
            "checks a job's status to determine if it has completed, failed, or is still running. "
            "The frequency of status checks is determined by this configuration option. Setting an "
            "appropriate value helps to monitor job progress without generating too many API calls or "
            "consuming too many resources. It's advisable to use the default value and avoid changing it."
        ),
    )
    config_builder.add(
        key=DAGS_MAX_CONCURRENT_RUNNING_JOBS,
        default_value=15,
        description=(
            "This sets the maximum number of concurrent running jobs. When at full capacity, any ready-to-start job "
            "would be delayed until a running job is completed. The limit is determined by this configuration option. "
            "Setting an appropriate value helps to limit the generation of too many API calls or consuming too many "
            "resources. It's advisable to use the default value for this variable."
        ),
    )
