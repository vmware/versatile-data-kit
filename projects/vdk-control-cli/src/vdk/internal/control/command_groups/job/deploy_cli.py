# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import os
from enum import Enum
from enum import unique
from typing import Optional

import click
from vdk.internal.control.command_groups.job.deploy_cli_impl import JobDeploy
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import get_or_prompt


@unique
class DeployOperation(Enum):
    """
    An enum used to store the types of deploy operations
    """

    CREATE = "create"
    UPDATE = "update"
    REMOVE = "remove"
    SHOW = "show"


@click.command(
    help="Deploy a Data Job. "
    "Deployment takes both the build/code (job's directory) "
    "and the deploy specific properties (config.ini) "
    "and is ready for immediate execution in the execution environment"
    """

Examples:

\b
# This will deploy the Data Job in directory example-job (it takes a few minutes)
# You will be prompted to confirm job name
vdk deploy -p /home/user/data-jobs/example-job

\b
# Then we can check what is the latest deployed version
vdk deploy --show -n example-job -t job-team

\b
# Disable a Data Job
vdk deploy --disable -n example-job -t job-team

\b
# Deploy job and wait until deployed
new_version=`vdk deploy -p /home/user/data-jobs/example-job -o json | jq '.job_version'`
while ! vdk deploy --show -o json -n example-job -t job-team | grep $new_version ; do echo "waiting ..."; sleep 10; done

\b
# Deploy multiple Data Jobs in a single command
echo "Job1
job2
job3" | xargs -I {JOB} vdk deploy  -t job-team  -n {JOB} –p <PARENT_DIR_TO_JOBS>/{JOB}

\b
# Experimental. Update job version (for example rollback quickly to latest stable version)
vdk deploy --update --job-version <job-version-here> -n example-job -t job-team
               """
)
@click.option("-n", "--name", type=click.STRING, help="The Data Job name.")
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    help="The team name to which the job should belong to.",
)
@click.option(
    "--create",
    "operation",
    flag_value=DeployOperation.CREATE,
    default=True,
    help="Create a new deployment of a Data Job. "
    "You must set job path (--job-path) with the directory of the Data Job. "
    "If there is a currently executing Data Job with the previous deployment version it will continue "
    "until its execution is finished. "
    "Any subsequent execution will use the new deployment. "
    "If there are no changes of the Data Job, no new version is created. "
    "--create is the default behaviour of the deploy command so you can generally omit this flag.",
)
@click.option(
    "--remove",
    "operation",
    flag_value=DeployOperation.REMOVE,
    help="Remove a deployment, so job will not be scheduled any more for execution. "
    "Currently running job will be allowed to finish.",
)
@click.option(
    "--update",
    "operation",
    hidden=True,
    flag_value=DeployOperation.UPDATE,
    help="Update specified deployment version of a Data Job for a cloud execution. "
    "It is used to revert to previous version. "
    "Deploy specific configuration will not be updated. "
    "You need to specify --job-version and/or --vdk-version. "
    "The option is experimental",
)
@click.option(
    "--enable",
    "enabled",
    flag_value=True,
    default=None,
    help="Enable a job. That will basically un-pause the job.",
)
@click.option(
    "--disable",
    "enabled",
    flag_value=False,
    default=None,
    help="Disable a job. Will not schedule a new cloud execution. Effectively pausing the job. "
    "Currently running job will be allowed to finish.",
)
@click.option(
    "--show",
    "operation",
    flag_value=DeployOperation.SHOW,
    help="Shows details about deployed job.",
)
@click.option(
    "-p",
    "--job-path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True),
    help="Path to the job directory. It must contain at least properly configured config.ini file.",
)
@click.option(
    "-v",
    "--job-version",
    type=click.STRING,
    hidden=True,
    help="The job version (Git Commit) of the job. The job must have been deployed first (see --create).",
)
@click.option(
    "-v",
    "--vdk-version",
    type=click.STRING,
    hidden=True,
    help="The vdk version to be used in a cloud run."
    "It must be the same vdk python distribution that is installed by Control Service operators. "
    "To check for possible versions see vdk distribution docker image tags. "
    "Assuming each released python distribution has a corresponding image "
    "check with pip index versions vdk-distribution-name. "
    "The option is valid only when used alongside --update otherwise it's ignored."
    "The option is experimental.",
)
@click.option(
    "-r",
    "--reason",
    help="Add a reason message for the job deploy. "
    "The flag works only in combination with the create flag (--create). "
    "The reason will be shown in the commit message in the git repo where the jobs are stored. "
    "Make sure you surround the reason with double quotes to avoid errors.",
)
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def deploy(
    name: str,
    team: str,
    job_version: str,
    vdk_version: str,
    enabled: Optional[bool],
    job_path: str,
    operation: str,
    reason: str,
    rest_api_url: str,
    output: str,
):
    cmd = JobDeploy(rest_api_url, output)
    if operation == DeployOperation.UPDATE or enabled is not None:
        name = get_or_prompt("Job Name", name)
        team = get_or_prompt("Job Team", team)
        # default to ask for job version to update
        if not vdk_version and not job_version and enabled is None:
            job_version = get_or_prompt("Job Version", job_version)
        return cmd.update(name, team, enabled, job_version, vdk_version, output)
    if operation == DeployOperation.REMOVE:
        name = get_or_prompt("Job Name", name)
        team = get_or_prompt("Job Team", team)
        return cmd.remove(name, team)
    if operation == DeployOperation.SHOW:
        name = get_or_prompt("Job Name", name)
        team = get_or_prompt("Job Team", team)
        return cmd.show(name, team, output)
    if operation == DeployOperation.CREATE:
        job_path = get_or_prompt("Job Path", job_path)
        default_name = os.path.basename(job_path)
        name = get_or_prompt("Job Name", name, default_name)
        reason = get_or_prompt("Reason", reason)
        return cmd.create(name, team, job_path, reason, output)
