# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
from typing import List

import click
from taurus_datajob_api import ApiException
from taurus_datajob_api import DataJob
from taurus_datajob_api import DataJobDeploymentStatus
from taurus_datajob_api import DataJobExecution
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import OutputFormat

log = logging.getLogger(__name__)


class JobShow:
    def __init__(self, rest_api_url: str, output: str):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()
        self.deploy_api = ApiClientFactory(rest_api_url).get_deploy_api()
        self.execution_api = ApiClientFactory(rest_api_url).get_execution_api()
        self.output = output

    def __read_data_job(self, name: str, team: str) -> DataJob:
        try:
            return self.jobs_api.data_job_read(team_name=team, job_name=name)
        except ApiException as e:
            raise VDKException(
                what=f"Cannot find data job {name}",
                why="Data job does not exist on CLOUD.",
                consequence="Cannot show job details.",
                countermeasure="Use VDK CLI create command to create the job first.",
            ) from e

    def __read_deployments(
        self, job_name: str, team: str
    ) -> List[DataJobDeploymentStatus]:
        return self.deploy_api.deployment_list(team_name=team, job_name=job_name)

    def __read_executions(self, job_name: str, team: str) -> List[DataJobExecution]:
        return self.execution_api.data_job_execution_list(
            team_name=team, job_name=job_name
        )

    @ApiClientErrorDecorator()
    def show_job(self, job_name: str, team: str) -> None:
        job = self.__read_data_job(job_name, team)
        deployments = self.__read_deployments(job_name, team)
        executions = self.__read_executions(job_name, team)

        job_as_dict = job.to_dict()
        job_as_dict["deployments"] = list(map(lambda d: d.to_dict(), deployments))
        job_as_dict["executions"] = list(map(lambda e: e.to_dict(), executions))[:2]

        click.echo(cli_utils.json_format(job_as_dict, indent=2))


@click.command(
    name="show",
    help="Show data job definition deployments if any and recent (2) executions. "
    "The format of the data is same one as returned by backend API."
    """

Examples:

\b
# List all jobs for team taurus
vdk show -n job-name -t team-name
                """,
    hidden=True,
)
@click.option(
    "-n", "--name", prompt="Job Name", type=click.STRING, help="The job name."
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The name of the team that Data Jobs belong to in the searched list.",
)
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def show_command(name: str, team: str, rest_api_url: str, output: str):
    cmd = JobShow(rest_api_url, output)
    cmd.show_job(name, team)
