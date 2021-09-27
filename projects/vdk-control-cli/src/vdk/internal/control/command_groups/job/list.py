# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import datetime
import json
import logging
from enum import Enum
from enum import unique
from typing import Dict
from typing import List

import click
from tabulate import tabulate
from taurus_datajob_api import DataJobQueryResponse
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import GqlQueryBuilder
from vdk.internal.control.utils.cli_utils import OutputFormat

log = logging.getLogger(__name__)


class JobList:
    def __init__(self, rest_api_url: str):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()

    @ApiClientErrorDecorator()
    def list_jobs(
        self, team: str, jobs_for_all_teams: bool, more_details: int, output: str
    ):
        has_more_jobs = True
        page_number = 1
        page_size = 100

        jobs = []

        while has_more_jobs:
            response: DataJobQueryResponse = self.jobs_api.jobs_query(
                query=self.build_jobs_query(
                    page_number=page_number,
                    page_size=page_size,
                    team_name=team,
                    show_all=jobs_for_all_teams,
                    more_details=more_details,
                ),
                team_name=team,
            )
            log.debug(f"Response: {response}")
            next_page: List[Dict] = response.data.content
            if next_page and len(next_page) > 0:
                jobs.extend(next_page)
            if len(next_page) < page_size:
                has_more_jobs = False
            page_number += 1

        jobs = list(map(self.job_to_dict, jobs))
        if output == OutputFormat.TEXT.value:
            if len(jobs) > 0:
                click.echo(tabulate(jobs, headers="keys"))
            else:
                click.echo("No Data Jobs.")
        else:
            click.echo(json.dumps(list(jobs)))

    @staticmethod
    def job_to_dict(job: Dict):
        # TODO: response model should come from open api client
        res = dict(
            job_name=job["jobName"],
            job_team=job["config"]["team"],
        )
        deployments = job.get("deployments", [])
        if deployments:
            res["status"] = "ENABLED" if deployments[0]["enabled"] else "DISABLED"
            if (
                "schedule" in job["config"]
                and "scheduleCron" in job["config"]["schedule"]
            ):
                res["schedule_cron"] = job["config"]["schedule"]["scheduleCron"]
                if (
                    res["status"] == "ENABLED"
                    and "nextRunEpochSeconds" in job["config"]["schedule"]
                ):
                    next_run = job["config"]["schedule"]["nextRunEpochSeconds"]
                    res["next_expected_run"] = datetime.datetime.fromtimestamp(next_run)
            if "status" in deployments[0] and deployments[0]["status"]:
                res["last_deployment_status"] = deployments[0]["status"]
            if "jobVersion" in deployments[0]:
                res["job_version"] = deployments[0]["jobVersion"]
            if "lastDeployedBy" in deployments[0]:
                res["deployed_by"] = deployments[0]["lastDeployedBy"]
            if "lastDeployedDate" in deployments[0]:
                res["deployed_date"] = deployments[0]["lastDeployedDate"]
        else:
            res["status"] = "NOT_DEPLOYED"
        if "contacts" in job["config"]:
            contacts = job["config"]["contacts"]
            if "notifiedOnJobSuccess" in contacts:
                res["notified_on_success"] = contacts["notifiedOnJobSuccess"]
            if "notifiedOnJobFailureUserError" in contacts:
                res["notified_on_user_error"] = contacts[
                    "notifiedOnJobFailureUserError"
                ]
            if "notifiedOnJobFailurePlatformError" in contacts:
                res["notified_on_platform_error"] = contacts[
                    "notifiedOnJobFailurePlatformError"
                ]
            if "notifiedOnJobDeploy" in contacts:
                res["notified_on_deploy"] = contacts["notifiedOnJobDeploy"]

        return res

    @staticmethod
    def build_jobs_query(
        page_number: int,
        page_size: int,
        team_name: str,
        show_all: bool,
        more_details: int,
    ):
        # TODO: query model should come from the open api client
        jobs_builder = GqlQueryBuilder()
        arguments = dict(pageNumber=page_number, pageSize=page_size)
        if not show_all and team_name:
            arguments["filter"] = (
                '[{ property: "config.team", pattern: "' + team_name + '", sort: ASC },'
                ' { property: "jobName", sort: ASC }]'
            )
        else:
            arguments["filter"] = (
                '[{ property: "config.team", sort: ASC },'
                ' { property: "jobName", sort: ASC }]'
            )

        jobs_content = (
            jobs_builder.start()
            .add_return_new("jobs", arguments=arguments)
            .add_return_new("content")
        )
        jobs_content.add("jobName")
        jobs_config = jobs_content.add_return_new("config")
        jobs_config.add("team").add("description")
        jobs_config.add_return_new("schedule").add(
            "scheduleCron"
        )  # .add('nextRunEpochSeconds') not released, yet
        jobs_deployments = (
            jobs_content.add_return_new("deployments").add("enabled").add("status")
        )
        if more_details >= 1:
            jobs_deployments.add("jobVersion").add("lastDeployedBy").add(
                "lastDeployedDate"
            )

        if more_details >= 2:
            job_contacts = jobs_config.add_return_new("contacts")
            job_contacts.add("notifiedOnJobDeploy").add("notifiedOnJobSuccess").add(
                "notifiedOnJobFailurePlatformError"
            ).add("notifiedOnJobFailureUserError")

        query = jobs_builder.build()
        log.debug("Jobs list (graphql) query: " + query)
        return query


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


class NotRequiredIfAllOperationExists(click.Option):
    def handle_parse_result(self, ctx, opts, args):
        if "operation_all" in opts:
            self.required = None
            self.prompt = None

        return super().handle_parse_result(ctx, opts, args)


@unique
class FilterOperation(Enum):
    """
    An enum used to store the types of filter operations
    """

    ALL = "all"


@click.command(
    name="list",
    help="List Data Jobs that have been created in cloud."
    """

Examples:

\b
# List all jobs for team taurus
vdk list -t taurus

\b
# List all jobs for team taurus in json format
vdk list -t taurus -o json
                """,
)
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    cls=NotRequiredIfAllOperationExists,
    required=True,
    prompt="Job Team",
    help="The name of the team that Data Jobs belong to in the searched list."
    " Not required if (-a,--all) option is provided.",
)
@click.option(
    "-a",
    "--all",
    "operation_all",
    flag_value=FilterOperation.ALL.value,
    default=False,
    help="Include the Data Jobs for all the teams."
    " If provided the team name(-t,--team) will not be required.",
)
@click.option(
    "-m",
    "--more-details",
    hidden=True,
    count=True,
    help="Include more details about the jobs. Specify the flag multiple times to make the output even more verbose .",
)
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def list_command(
    team: str, operation_all: str, more_details: int, rest_api_url: str, output: str
):
    cmd = JobList(rest_api_url)
    if team is None:
        team = "no-team-specified"
    cmd.list_jobs(
        team, (operation_all == FilterOperation.ALL.value), more_details, output
    )
    pass
