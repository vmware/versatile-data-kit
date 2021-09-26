# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging

import click
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils

log = logging.getLogger(__name__)


# TODO: handle errors messages more gracefully (do not show stacktrace, show http body access_token_request_response)


class JobDelete:
    def __init__(self, rest_api_url: str):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()

    @ApiClientErrorDecorator()
    def delete_job(self, name: str, team: str):
        log.debug(f"Delete data job {name} of team {team}")
        self.jobs_api.data_job_delete(team_name=team, job_name=name)
        log.info(
            f"Deleted Data Job {name} and all its deployments successfully."
            f" The job's folder may still be present on your local file system."
        )


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    help="Delete a Data Job from the cloud. "
    "This will remove all deployed instances and free all resources for the job "
    "(including any provision keytab credentials and permissions for the Data Job will be revoked). "
    "The local directory of the job will not be deleted."
)
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    required=True,
    prompt="Job Name",
    help="The Data Job name.",
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The team name to which the job belong to.",
)
@click.confirmation_option(prompt="Are you sure you want to delete the data job?")
@cli_utils.rest_api_url_option()
@cli_utils.check_required_parameters
def delete(name: str, team: str, rest_api_url: str):
    cmd = JobDelete(rest_api_url)
    cmd.delete_job(name, team)
    pass
