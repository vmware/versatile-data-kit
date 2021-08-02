# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import click
import click_spinner
from taurus.vdk.control.configuration.defaults_config import load_default_team_name
from taurus.vdk.control.exception.vdk_exception import VDKException
from taurus.vdk.control.job.job_archive import JobArchive
from taurus.vdk.control.rest_lib.factory import ApiClientFactory
from taurus.vdk.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from taurus.vdk.control.utils import cli_utils

log = logging.getLogger(__name__)


class JobDownloadSource:
    def __init__(self, rest_api_url):
        self.sources_api = ApiClientFactory(rest_api_url).get_jobs_sources_api()
        self.__job_archive = JobArchive()

    @ApiClientErrorDecorator()
    def download(self, team, name, path):
        log.debug(f"Download job {name} of team {team} into parent {path}")
        self.__validate_job_path(path, name)
        job_archive_path = os.path.join(path, f"{name}.zip")
        try:
            log.info(f"Downloading data job {name} in {path}/{name} ...")
            with click_spinner.spinner():
                response = self.sources_api.data_job_sources_download(
                    team_name=team, job_name=name, _preload_content=False
                )
                self.__write_response_to_archive(job_archive_path, response)
                self.__job_archive.unarchive_data_job(
                    job_name=name, job_archive_path=job_archive_path, job_directory=path
                )

            log.info(f"Downloaded Data Job in {path}/{name}")
        finally:
            self.__cleanup_archive(job_archive_path)

    @staticmethod
    def __write_response_to_archive(job_archive_path, response):
        log.debug(f"Write data job source to {job_archive_path}")
        with open(job_archive_path, "wb") as w:
            w.write(response.data)

    @staticmethod
    def __validate_job_path(path, name):
        if path is None:
            path = os.path.abspath(".")
        job_path = os.path.join(path, name)
        if os.path.exists(job_path):
            raise VDKException(
                what=f"Cannot download data job source at given job path: {path}",
                why=f"Directory with name {name} already exists.",
                consequence="Cannot download the job and will abort.",
                countermeasure=f"Delete or move directory {job_path} or change --path location",
            )
        return job_path

    @staticmethod
    def __cleanup_archive(archive_path):
        try:
            os.remove(archive_path)
        except OSError as e:
            log.warning(
                VDKException(
                    what=f"Cannot cleanup archive: {archive_path} as part of deployment.",
                    why=f"VDK CLI did not clean up after deploying: {e}",
                    consequence="There is a leftover archive file next to the folder containing the data job",
                    countermeasure="Clean up the archive file manually or leave it",
                )
            )


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    name="download-job",
    help="Download Data Job source directory. It's a directory with the data job content inside.",
)
@click.option(
    "-n",
    "--name",
    type=click.STRING,
    required=True,
    prompt="Job Name",
    help="The job name.",
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
@click.option(
    "-p",
    "--path",
    type=click.Path(exists=True, resolve_path=True),
    required=False,
    prompt="Path to the data job directory",
    default=".",
    show_default=True,
    help="The path to the parent directory where the Data Job will be downloaded."
    " If none specified it will use the current working directory.",
)
@cli_utils.rest_api_url_option()
@cli_utils.check_required_parameters
def download_job(name, team, path, rest_api_url):
    cmd = JobDownloadSource(rest_api_url)
    cmd.download(team, name, path)


# TODO: download all jobs for a team
# TODO: download old version of a job? list all versions ?
