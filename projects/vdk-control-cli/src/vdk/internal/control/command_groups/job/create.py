# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os
import pathlib
from typing import Optional
from typing import Tuple

import click
from taurus_datajob_api import ApiException
from taurus_datajob_api import DataJob
from taurus_datajob_api import DataJobConfig
from taurus_datajob_api import DataJobSchedule
from vdk.internal.control.command_groups.job.download_key import JobDownloadKey
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.configuration.vdk_config import VDKConfig
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.job.job_config import JobConfig
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils

log = logging.getLogger(__name__)


class JobCreate:
    def __init__(self, rest_api_url: str):
        self.__rest_api_url = rest_api_url
        self.__vdk_config = VDKConfig()

    @ApiClientErrorDecorator()
    def create_job(
        self, name: str, team: str, path: str, cloud: bool, local: bool
    ) -> None:
        self.__validate_job_name(name)
        if local:
            self.validate_job_path(path, name)

        if cloud:
            self.__create_cloud_job(team, name)
        if local:
            job_path = self.__get_job_path(path, name)
            self.__create_local_job(team, name, job_path)
            if cloud:
                self.__download_key(team, name, path)

    def __create_cloud_job(self, team: str, name: str) -> None:
        jobs_api = ApiClientFactory(self.__rest_api_url).get_jobs_api()
        job_config = DataJobConfig(schedule=DataJobSchedule())
        # TODO: currently there's bug and description is not persisted, so it's not exposed to CLI for now
        job = DataJob(job_name=name, team=team, description="", config=job_config)
        log.debug(f"Create data job {name} of team {team}: {job}")
        try:
            jobs_api.data_job_create(team_name=team, data_job=job, name=name)
        except ApiException as e:
            if e.status == 409:
                log.warning(
                    f"Data Job with name {name} already exists in cloud runtime."
                )
            else:
                raise
        log.info(
            f"Data Job with name {name} created and registered in cloud runtime by Control Service."
        )

    def __create_local_job(self, team: str, name: str, job_path: str) -> None:
        sample_job = self.__vdk_config.sample_job_directory
        log.debug(f"Create sample job from directory: {sample_job} into {job_path}")
        cli_utils.copy_directory(sample_job, job_path)
        local_config = JobConfig(job_path)
        if not local_config.set_team_if_exists(team):
            log.warning(f"Failed to write Data Job team {team} in config.ini.")
        log.info(f"Data Job with name {name} created locally in {job_path}.")

    def __download_key(self, team, name, path):
        job_download_key = JobDownloadKey(self.__rest_api_url)
        try:
            log.info("Will download keytab of the job now ...")
            job_download_key.download(team, name, path)
        except Exception as e:
            log.warning(
                VDKException(
                    what=f"Could not download keytab for data job: {name}",
                    why=f"Error is: {e}",
                    consequence="Local execution of the job might fail since the job may not have permissions to some resources",
                    countermeasure="Try to manually download the data job keytab with vdk",
                ).message
            )

    def validate_job_path(self, path: str, name: str) -> None:
        self.__get_job_path(path, name)

    @staticmethod
    def __get_job_path(path: str, name: str) -> str:
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
    def __validate_job_name(job_name: str) -> None:
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
    help="""Create a new Data Job in cloud and/or locally.

Examples:

\b
# Simplest form which will prompt for necessary info:
# It will create it locally and created in cloud
# only if there is a Control Service configured.
vdk create

\b
# Create data job in cloud runtime registering it in the Control Service.
# This will make it possible to use Control Service functionalities.
vdkcli create --cloud

\b
# Create local data job folder (from a sample).
vdkcli create --local

\b
# You can also specify both - in this case it will create it locally and in cloud
vdkcli create --local --cloud

\b
# Create a Data Job without prompts by specifying all necessary fields
# This will create a Data Job with name "example" that belongs to team 'super-team'
# and create a sample template of the job in /home/user/data-jobs/example-job
vdk create -n example-job -t super-team -p /home/user/data-jobs

"""
)
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    help="The data job name. It must be between 6 and 45 characters: lowercase or dash.",
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
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
    "--cloud",
    "--no-sample",
    "--no-template",
    type=click.STRING,
    is_flag=True,
    default=None,
    help="Will not create sample job on local file system (--path parameter is ignored in this case). "
    "Will only register it in the cloud Control service."
    "--no-sample and --no-template are deprecated. Prefer to use --cloud.",
)
@click.option(
    "--local",
    type=click.STRING,
    is_flag=True,
    default=None,
    help="Create sample job on local file system (--path parameter is required in this case).",
)
@cli_utils.rest_api_url_option()
def create(
    name: str,
    team: str,
    path: str,
    cloud: Optional[bool],
    local: Optional[bool],
    rest_api_url: str,
) -> None:
    cmd = JobCreate(rest_api_url)

    cloud, local = __determine_cloud_local_flags(cloud, local, rest_api_url)

    if cloud:
        cli_utils.check_rest_api_url(rest_api_url)

    name = cli_utils.get_or_prompt("Job Name", name)
    team = cli_utils.get_or_prompt("Job Team", team)
    if local:
        path = cli_utils.get_or_prompt(
            "Path to where sample data job will be created locally",
            path,
            os.path.abspath("."),
        )
        cmd.validate_job_path(path, name)

    cmd.create_job(name, team, path, cloud, local)
    pass


def __determine_cloud_local_flags(
    cloud: Optional[bool], local: Optional[bool], rest_api_url: str
) -> Tuple[bool, bool]:
    # determine if we are running create in local or in cloud or in both modes
    # local would only create sample job
    # cloud would only create job in Control Service
    # both - would do both
    # if user has explicitly passed cloud and not local we create only job on cloud
    if cloud and local is None:
        local = False
    # if user has explicitly passed local and not cloud we create job only locally
    if local and cloud is None:
        cloud = False
    # otherwise if user have not specified anything we create job on cloud if rest api url is set only and locally
    # always.
    if cloud is None:
        cloud = rest_api_url is not None and rest_api_url != ""
    if local is None:
        local = True
    return cloud, local
