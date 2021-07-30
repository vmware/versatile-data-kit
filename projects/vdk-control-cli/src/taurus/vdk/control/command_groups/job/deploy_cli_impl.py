# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import glob
import json
import logging
import os

import click
import click_spinner
from tabulate import tabulate
from taurus.vdk.control.configuration.defaults_config import load_default_team_name
from taurus.vdk.control.exception.vdk_exception import VDKException
from taurus.vdk.control.job.job_archive import JobArchive
from taurus.vdk.control.job.job_config import JobConfig
from taurus.vdk.control.rest_lib.factory import ApiClientFactory
from taurus.vdk.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from taurus.vdk.control.utils.cli_utils import get_or_prompt
from taurus.vdk.control.utils.cli_utils import OutputFormat
from taurus_datajob_api import ApiException
from taurus_datajob_api import DataJob
from taurus_datajob_api import DataJobConfig
from taurus_datajob_api import DataJobContacts
from taurus_datajob_api import DataJobDeployment
from taurus_datajob_api import DataJobSchedule
from taurus_datajob_api import Enable

log = logging.getLogger(__name__)


class JobDeploy:
    ZIP_ARCHIVE_TYPE = "zip"
    ARCHIVE_SUFFIX = "-archive"

    def __init__(self, rest_api_url, output):
        self.deploy_api = ApiClientFactory(rest_api_url).get_deploy_api()
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()
        self.job_sources_api = ApiClientFactory(rest_api_url).get_jobs_sources_api()
        # support for multiple deployments is not implemented yet so we can put anything here.
        # Ultimately this will be user facing parameter (possibly fetched from config.ini)
        self.__deployment_id = "production"
        self.__job_archive = JobArchive()

    @staticmethod
    def __detect_keytab_files_in_job_directory(job_path):
        keytab_glob = os.path.join(job_path, "**/*.keytab")
        keytab_files = glob.glob(keytab_glob, recursive=True)
        if keytab_files:
            raise VDKException(
                what=f"Detected keytab file inside data job directory.: {keytab_files}",
                why="Keytab files are secret and must be kept separate - usually at the same level as data job directory but not inside.",
                consequence="In order to prevent security issues, data job code will not be uploaded and deploy operation is aborted.",
                countermeasure="Move the keytab file outside data job directory and try to deploy again.",
            )

    @staticmethod
    def __validate_datajob(job_path, job_config, team):
        log.debug(
            "Validate data job does not have credentials in its directory (keytab file)"
        )
        JobDeploy.__detect_keytab_files_in_job_directory(job_path)

        log.debug("Validate data job team is consistent.")
        job_config_team = job_config.get_team()
        if team is not None and job_config_team is not None and team != job_config_team:
            raise VDKException(
                what="Cannot create new deployment of the data job.",
                why=f"Team param ({team}) and team value in config.ini ({job_config_team}) do not match.",
                consequence="The latest change is not deployed, job will continue to run with previous version.",
                countermeasure=f"1. Fix config.ini to set correct team (if it is {team}) OR\n"
                f"2. Do not pass team param (team {job_config_team} will be automatically used from config.ini) OR\n"
                f"3. Pass param team={job_config_team} OR\n"
                f"4. Create a new job with team={team} and try to deploy it\n",
            )

        # TODO: we may use https://github.com/Yelp/detect-secrets to make sure users do not accidentally pass secrets

    @staticmethod
    def __check_value(key, value):
        if not value:
            raise VDKException(
                what="Cannot extract job configuration.",
                why=f"Configuration property {key} in file config.ini is missing.",
                consequence="Cannot deploy the Data Job.",
                countermeasure="Update config.ini.",
            )
        return value

    def __read_data_job(self, name, team):
        try:
            return self.jobs_api.data_job_read(team_name=team, job_name=name)
        except ApiException as e:
            raise VDKException(
                what=f"Cannot find data job {name}",
                why="Data job does not exist on CLOUD.",
                consequence="Cannot deploy the Data Job.",
                countermeasure="Use VDK CLI create command to create the job first.",
            ) from e

    @staticmethod
    def __archive_binary(job_archive_path):
        log.debug(f"Read archive binary: {job_archive_path}")
        with open(job_archive_path, "rb") as job_archive_file:
            # Read the whole file at once
            job_archive_binary = job_archive_file.read()
            return job_archive_binary

    @staticmethod
    def __cleanup_archive(archive_path):
        try:
            log.debug(f"Remove temp archive {archive_path}")
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

    def __update_data_job_deploy_configuration(self, job_path, name, team):
        job: DataJob = self.__read_data_job(name, team)
        local_config = JobConfig(job_path)
        schedule = self.__check_value("schedule_cron", local_config.get_schedule_cron())
        contacts = DataJobContacts(
            local_config.get_contacts_notified_on_job_failure_user_error(),
            local_config.get_contacts_notified_on_job_failure_platform_error(),
            local_config.get_contacts_notified_on_job_success(),
            local_config.get_contacts_notified_on_job_deploy(),
        )
        job.config = DataJobConfig(
            enable_execution_notifications=local_config.get_enable_execution_notifications(),
            notification_delay_period_minutes=local_config.get_notification_delay_period_minutes(),
            contacts=contacts,
            schedule=DataJobSchedule(schedule_cron=schedule),
        )
        log.debug(f"Update data job deploy configuration: {job}")
        self.jobs_api.data_job_update(team_name=team, job_name=name, data_job=job)

    @ApiClientErrorDecorator()
    def update(self, name, team, job_version, output):
        deployment = DataJobDeployment(
            job_version=job_version, mode="release", enabled=True
        )
        log.debug(f"Update Deployment of a job {name} of team {team} : {deployment}")
        self.deploy_api.deployment_update(
            team_name=team, job_name=name, data_job_deployment=deployment
        )

        if output == OutputFormat.TEXT.value:
            log.info(
                f"Request to deploy Data Job {name} using version {job_version} finished successfully.\n"
                f"It would take a few minutes for the Data Job to be deployed in the server.\n"
                f"If notified_on_job_deploy option in config.ini is configured then "
                f"notification will be sent on successful deploy or in case of an error.\n"
                f"You can also vdkcli deploy --show to see if the job is deployed successfully."
            )
        else:
            result = {
                "job_name": name,
                "job_version": job_version,
            }
            click.echo(json.dumps(result))

    @ApiClientErrorDecorator()
    def disable(self, name, team):
        enable = Enable(enabled=False)
        log.debug(f"Disable Deployment of a job {name} of team {team}")
        self.deploy_api.deployment_enable(
            team_name=team,
            job_name=name,
            deployment_id=self.__deployment_id,
            enable=enable,
        )
        log.info(f"Deployment of Data Job {name} disabled.")

    @ApiClientErrorDecorator()
    def enable(self, name, team):
        enable = Enable(enabled=True)
        log.debug(f"Enable Deployment of a job {name} of team {team}")
        self.deploy_api.deployment_enable(
            team_name=team,
            job_name=name,
            deployment_id=self.__deployment_id,
            enable=enable,
        )
        log.info(f"Deployment of Data Job {name} enabled.")

    @ApiClientErrorDecorator()
    def remove(self, name, team):
        log.debug(f"Remove Deployment of a job {name} of team {team}")
        self.deploy_api.deployment_delete(
            team_name=team, job_name=name, deployment_id=self.__deployment_id
        )
        log.info(f"Deployment of Data Job {name} removed.")

    @ApiClientErrorDecorator()
    def show(self, name, team, output):
        log.debug(f"Get list of deployments for job {name} of team {team} ")
        deployments = self.deploy_api.deployment_list(team_name=team, job_name=name)
        log.debug(
            f"Found following deployments for job {name} of team {team} : {deployments}"
        )
        if deployments:
            # d.to_dict() brings unnecessary parts of data
            deployments = map(
                lambda d: dict(
                    job_name=name,
                    job_version=d.job_version,
                    last_deployed_by=d.last_deployed_by,
                    last_deployed_date=d.last_deployed_date,
                    enabled=d.enabled,
                ),
                deployments,
            )
            if output == OutputFormat.TEXT.value:
                click.echo("")
                click.echo(tabulate(deployments, headers="keys"))
            else:
                click.echo(json.dumps(list(deployments)))
        else:
            if output == OutputFormat.TEXT.value:
                click.echo("No deployments.")
            else:
                click.echo(json.dumps([]))

    @ApiClientErrorDecorator()
    def create(self, name, team, job_path, reason, output):
        log.debug(
            f"Create Deployment of a job {name} of team {team} with local path {job_path} and reason {reason}"
        )
        job_path = os.path.abspath(job_path)
        if not os.path.isdir(job_path):
            raise VDKException(
                what="Cannot create new deployment of the data job.",
                why=f"Directory {job_path} does not exists.",
                consequence="The latest change is not deployed, job will continue to run with previous version",
                countermeasure="Provide correct path to the Data Job.",
            )

        log.debug(
            "We verify that config.ini exists. This is to avoid uploading accidentally some random directory"
        )
        job_config = JobConfig(job_path)

        self.__validate_datajob(job_path=job_path, job_config=job_config, team=team)
        team = get_or_prompt(
            "Team Name", team or job_config.get_team() or load_default_team_name()
        )

        if output == OutputFormat.TEXT.value:
            log.info(
                f"Deploy Data Job with name {name} from directory {job_path} ... \n"
            )

        archive_path = self.__job_archive.archive_data_job(
            job_name=name, job_archive_path=job_path
        )
        try:
            job_archive_binary = self.__archive_binary(archive_path)

            if output == OutputFormat.TEXT.value:
                log.info("Uploading the data job might take some time ...")
            with click_spinner.spinner(disable=(output == OutputFormat.JSON.value)):
                data_job_version = self.job_sources_api.sources_upload(
                    team_name=team,
                    job_name=name,
                    body=job_archive_binary,
                    reason=reason,
                )

            self.__update_data_job_deploy_configuration(job_path, name, team)
            self.update(name, team, data_job_version.version_sha, output)
        finally:
            self.__cleanup_archive(archive_path=archive_path)
