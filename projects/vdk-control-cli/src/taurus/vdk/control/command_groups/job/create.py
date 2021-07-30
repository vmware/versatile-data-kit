# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib

import click
from taurus.vdk.control.command_groups.job.download_key import JobDownloadKey
from taurus.vdk.control.configuration.defaults_config import load_default_team_name
from taurus.vdk.control.configuration.vdk_config import VDKConfig
from taurus.vdk.control.exception.vdk_exception import VDKException
from taurus.vdk.control.job.job_config import JobConfig
from taurus.vdk.control.rest_lib.factory import ApiClientFactory
from taurus.vdk.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from taurus.vdk.control.utils import cli_utils
from taurus_datajob_api import ApiException
from taurus_datajob_api import DataJob
from taurus_datajob_api import DataJobConfig
from taurus_datajob_api import DataJobSchedule

log = logging.getLogger(__name__)


class JobCreate:
    def __init__(self, rest_api_url: str):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()
        self.job_download_key = JobDownloadKey(rest_api_url)
        self.vdk_config = VDKConfig()

    @ApiClientErrorDecorator()
    def create_job(self, name: str, team: str, path: str, no_sample: bool):
        self.validate_job_name(name)

        if not no_sample:
            job_path = self.get_job_path(path, name)

        job_config = DataJobConfig(schedule=DataJobSchedule())
        # TODO: currently there's bug and description is not persisted, so it's not exposed to CLI for now
        job = DataJob(job_name=name, team=team, description="", config=job_config)
        log.debug(f"Create data job {name} of team {team}: {job}")
        try:
            self.jobs_api.data_job_create(team_name=team, data_job=job, name=name)
        except ApiException as e:
            if e.status == 409:
                log.warning(
                    f"Data Job with name {name} already exists in cloud runtime."
                )
            else:
                raise

        if not no_sample:
            sample_job = self.vdk_config.get_sample_job_directory
            log.debug(f"Create sample job from directory: {sample_job} into {job_path}")
            cli_utils.copy_directory(sample_job, job_path)
            local_config = JobConfig(job_path)
            if not local_config.set_team_if_exists(team):
                log.warning(f"Failed to write Data Job team {team} in config.ini.")

            log.info(f"Data Job with name {name} created in {job_path}.")

            try:
                log.info("Will download keytab of the job now ...")
                self.job_download_key.download(team, name, path)
            except Exception as e:
                log.warning(
                    VDKException(
                        what=f"Could not download keytab for data job: {name}",
                        why=f"Error is: {e}",
                        consequence="Local execution of the job might fail since the job may not have permissions to some resources",
                        countermeasure="Try to manually download the data job keytab with vdkcli",
                    )
                )
        else:
            log.info(f"Data Job with name {name} created.")

    @staticmethod
    def get_job_path(path: str, name: str) -> str:
        if path is None:
            path = os.path.abspath(".")
        log.debug(f"Parent path of job is {path}")
        if not os.path.isdir(path):
            raise VDKException(
                what=f"Cannot create job at passed as argument path (job directory): {path} ",
                why=f"The directory does not exist.",
                consequence="Cannot create the data job as it's used to place inside the data job directory.",
                countermeasure="Create the missing directories "
                "OR change --path location "
                "OR skip creating sample job with --no-sample option",
            )

        job_path = os.path.join(path, name)
        if os.path.exists(job_path):
            raise VDKException(
                what=f"Cannot create job at given job path: {job_path}",
                why=f"Target job directory already exists.",
                consequence="Cannot create the new job.",
                countermeasure="Delete/move directory or change --path location",
            )
        return job_path

    @staticmethod
    def validate_job_name(job_name):
        countermeasure_str = (
            "Ensure that the job name is between 5 and 45 characters long, "
            "that it contains only alphanumeric characters and dashes, "
            "that it contains no uppercase characters, and that it begins with a letter."
        )
        name_without_dashes = "".join(
            [char if char != "-" else "" for char in job_name]
        )
        # tests if the name without dashes contains only alphanumeric symbols
        if not name_without_dashes.isalnum():
            raise VDKException(
                what=f"Cannot create job with name: {job_name}.",
                why="Job name must only contain alphanumerical symbols and dashes.",
                consequence="Cannot create the new job.",
                countermeasure=countermeasure_str,
            )
        # tests if name is lowercase
        name_without_dashes_or_nums = "".join(
            [char if char.isalpha() else "" for char in name_without_dashes]
        )
        if not all(
            [char.islower() for char in name_without_dashes_or_nums]
        ):  # check if all symbols are lowercase
            raise VDKException(
                what=f"Cannot create job with name: {job_name}.",
                why="Job name must only contain lowercase symbols.",
                consequence="Cannot create the new job.",
                countermeasure=countermeasure_str,
            )
        # tests if length is between 5 and 45
        if len(job_name) < 5 or len(job_name) > 45:
            raise VDKException(
                what=f"Cannot create job with name: {job_name}.",
                why="Job name length must be within 5 to 45 characters.",
                consequence="Cannot create the new job.",
                countermeasure=countermeasure_str,
            )
        # tests if name starts with a letter
        if not job_name[0].isalpha():
            raise VDKException(
                what=f"Cannot create job with name: {job_name}.",
                why="Job name must begin with a letter.",
                consequence="Cannot create the new job.",
                countermeasure=countermeasure_str,
            )


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    help="""Creates a new data job in cloud and locally.

Examples:

\b
# Simplest form and will prompt for necessary info:
vdkcli create

\b
# Create data job without creating local sample folder:
vdkcli create --no-sample

\b
# Create job without prompts by specifying all necessary fields
# This will create job with name "example" that belongs to team 'super-team'
# and create sample template of the job in /home/user/data-jobs/example-job
vdkcli create -n example-job -t super-team -p /home/user/data-jobs

"""
)
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    required=True,
    prompt="Job Name",
    help="The data job name. It must be between 6 and 45 characters: lowercase or dash.",
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The team name to which the job should belong to.",
)
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=False, resolve_path=True),
    help="The path to the parent directory of the Data Job."
    " If none specified it will use the current working directory."
    " New directory using job name will be created inside that path with sample job (unless --no-sample is used)."
    " Otherwise the keytab for the job will be placed into the directory.",
)
@click.option(
    "--no-sample",
    "--no-template",
    type=click.STRING,
    is_flag=True,
    default=False,
    show_default=True,
    help="Do not create sample job on local file system (--path parameter is ignored in this case).",
)
@cli_utils.rest_api_url_option()
@cli_utils.check_required_parameters
@click.pass_context
def create(ctx: click.Context, name, team, path, no_sample, rest_api_url):
    if not no_sample:
        path = cli_utils.get_or_prompt(
            "Path to where sample data job will be created locally",
            path,
            os.path.abspath("."),
        )
    cmd = JobCreate(rest_api_url)
    cmd.create_job(name, team, path, no_sample)
    pass
