# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import operator
import os
import sys
import webbrowser
from enum import Enum
from enum import unique
from typing import Optional

import click
import click_spinner
from tabulate import tabulate
from taurus_datajob_api import DataJobExecution
from taurus_datajob_api import DataJobExecutionLogs
from taurus_datajob_api import DataJobExecutionRequest
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.exception.vdk_exception import VDKException
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils
from vdk.internal.control.utils.cli_utils import get_or_prompt
from vdk.internal.control.utils.cli_utils import OutputFormat

log = logging.getLogger(__name__)


@unique
class ExecuteOperation(Enum):
    """
    An enum used to store the types of deploy operations
    """

    START = "start"
    CANCEL = "cancel"
    WAIT = "wait"
    SHOW = "show"
    LIST = "list"
    LOGS = "logs"


class JobExecute:
    def __init__(self, rest_api_url: str):
        self.__execution_api = ApiClientFactory(rest_api_url).get_execution_api()

    @staticmethod
    def __model_executions(executions, output: OutputFormat) -> str:
        def transform_execution(e: DataJobExecution):
            d = e.to_dict()
            d["job_version"] = e.deployment.job_version
            del d["deployment"]
            return d

        executions = list(map(lambda e: transform_execution(e), executions))

        if output == OutputFormat.TEXT.value:
            return tabulate(executions, headers="keys")
        elif output == OutputFormat.JSON.value:
            return cli_utils.json_format(list(executions))

    @staticmethod
    def __validate_and_parse_args(arguments: str) -> str:
        try:
            if arguments:
                return json.loads(arguments)
            else:
                return {}
        except Exception as e:
            vdk_ex = VDKException(
                what="Failed to validate job arguments.",
                why=str(e),
                consequence="I will not make the API call.",
                countermeasure="Make sure provided --arguments is a valid JSON string.",
            )
            raise vdk_ex

    @ApiClientErrorDecorator()
    def start(self, name: str, team: str, output: OutputFormat, arguments: str) -> None:
        execution_request = DataJobExecutionRequest(
            started_by=f"vdk-control-cli",
            args=self.__validate_and_parse_args(arguments),
        )
        log.debug(f"Starting job with request {execution_request}")
        _, _, headers = self.__execution_api.data_job_execution_start_with_http_info(
            team_name=team,
            job_name=name,
            deployment_id="production",  # TODO
            data_job_execution_request=execution_request,
        )
        log.debug(f"Received headers: {headers}")

        location = headers["Location"]
        execution_id = os.path.basename(location)
        if output == OutputFormat.TEXT.value:
            click.echo(
                f"Execution of Data Job {name} started. "
                f"See execution status using: \n\n"
                f"vdk execute --show --execution-id {execution_id} -n {name} -t {team}\n\n"
                f"See execution logs using: \n\n"
                f"vdk execute --logs --execution-id {execution_id} -n {name} -t {team}"
            )
        elif output == OutputFormat.JSON.value:
            result = {
                "job_name": name,
                "team": team,
                "execution_id": execution_id,
            }
            click.echo(json.dumps(result))

    @ApiClientErrorDecorator()
    def cancel(self, name: str, team: str, execution_id: str) -> None:
        click.echo("Cancelling data job execution. Might take some time...")
        with click_spinner.spinner():
            response = self.__execution_api.data_job_execution_cancel(
                team_name=team, job_name=name, execution_id=execution_id
            )
            log.debug(f"Response: {response}")
        click.echo("Job cancelled successfully.")

    @ApiClientErrorDecorator()
    def show(
        self, name: str, team: str, execution_id: str, output: OutputFormat
    ) -> None:
        execution: DataJobExecution = self.__execution_api.data_job_execution_read(
            team_name=team, job_name=name, execution_id=execution_id
        )
        click.echo(self.__model_executions([execution], output))

    @ApiClientErrorDecorator()
    def list(self, name: str, team: str, output: OutputFormat) -> None:
        executions: list[
            DataJobExecution
        ] = self.__execution_api.data_job_execution_list(team_name=team, job_name=name)
        click.echo(self.__model_executions(executions, output))

    def __get_execution_to_log(
        self, name: str, team: str, execution_id: str
    ) -> Optional[DataJobExecution]:
        if not execution_id:
            executions: list[
                DataJobExecution
            ] = self.__execution_api.data_job_execution_list(
                team_name=team, job_name=name
            )
            if not executions:
                return None
            log.info(
                "No execution id has been passed as argument. "
                "We will print the logs of the last started execution."
            )
            executions.sort(key=operator.attrgetter("start_time"), reverse=True)
            execution = executions[0]
        else:
            execution: DataJobExecution = self.__execution_api.data_job_execution_read(
                team_name=team, job_name=name, execution_id=execution_id
            )
        return execution

    @ApiClientErrorDecorator()
    def logs(self, name: str, team: str, execution_id: str) -> None:
        execution = self.__get_execution_to_log(name, team, execution_id)
        if not execution:
            log.info("No executions found.")
            return

        log.debug(f"Get execution details: {execution.to_dict()}")
        log.info(f"Logs for execution with id {execution.id} ...")
        if execution.logs_url:
            log.info(f"Opening browser to check logs at:\n{execution.logs_url}")
            is_open = webbrowser.open(execution.logs_url)
            if not is_open:
                log.info(
                    "We failed to open the browser automatically .\n"
                    f"Navigate manually in your favourite browser to {execution.logs_url} to find the execution logs."
                )
        else:
            log.debug("Fetch logs from Execution Current Logs API: ")
            logs: DataJobExecutionLogs = self.__execution_api.data_job_logs_download(
                team_name=team, job_name=name, execution_id=execution.id
            )
            click.echo(logs.logs)


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    help="Starts execution of a data job that is deployed or check status of job execution(s). (Beta)"
    """
Examples:

\b
# Start new remote execution of Data Job 'example-job'
# As an output it will print how to get starts and it's execution ID:
vdk execute --start -n example-job -t "Example Team"
\b
# Start a new remote execution of Data Job 'example-job' with extra arguments
# Arguments are passed to each step. Arguments must be a valid JSON object with key/value pairs.
vdk execute --start -n example-job -t "Example Team" --arguments '{"key1": "value1", "key2": "value2"}'

\b
# Check status of a currently executing Data Job:
vdk execute --show --execution-id example-job-1619094633811-cc49d  -n example-job -t "Example Team"

\b
# Cancel a currently executing Data Job:
vdk execute --cancel -t "Example Team" -n example-job --execution-id example-job-1619094633811-cc49d

\b
# List recent execution of a Data Job:
vdk execute --list -n example-job -t "Example Team"

\b
# We want to see the logs of the current execution that is running.
vdk execute --logs -n example-job -t "Example Team" --execution-id example-job-1619094633811-cc49d

""",
)
@click.option("-n", "--name", type=click.STRING, help="The job name.")
@click.option(
    "-t",
    "--team",
    type=click.STRING,
    default=load_default_team_name(),
    required=True,
    prompt="Job Team",
    help="The team name to which the job belong to.",
)
@click.option("-i", "--execution-id", type=click.STRING, help="The job execution ID.")
@click.option(
    "--start",
    "operation",
    flag_value=ExecuteOperation.START,
    help="Start execution of a Data Job. ",
)
@click.option(
    "--wait",
    "operation",
    hidden=True,
    flag_value=ExecuteOperation.WAIT,
    help="Wait for current job execution (if any) to finish "
    "(if specified execution id wait for execution with given id to finish)."
    "Require --execution-id to be provided. "
    "Should be printed when using vdk execute --start",
)
@click.option(
    "--cancel",
    "operation",
    flag_value=ExecuteOperation.CANCEL,
    help="Cancels a running or submitted Data Job execution. Requires --execution-id to be provided. "
    "Should be printed when using vdk execute --start",
)
@click.option(
    "--list",
    "operation",
    flag_value=ExecuteOperation.LIST,
    help="List recent and/or current executions of the Data Job. ",
)
@click.option(
    "--show",
    "operation",
    flag_value=ExecuteOperation.SHOW,
    help="Shows details Data Job Executions. Requires --execution-id to be provided. "
    "Should be printed when using vdk execute --start",
)
@click.option(
    "--logs",
    "operation",
    flag_value=ExecuteOperation.LOGS,
    help="Shows logs about Data Job Execution. It will either provide link to central logging system or"
    " print the logs locally."
    "If --execution-id is omitted, it will fetch logs from more recently started job execution."
    " --execution-id should be provided to get logs from specific job execution."
    "Execution id is printed when using vdk execute --start. "
    "You can also see execution id with vdk execute --list operation.",
)
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@click.option(
    "--arguments",
    type=click.STRING,
    required=False,
    help="Pass arguments when starting a data job. "
    "Those arguments will be passed to each step. "
    "Must be in valid JSON format",
)
@cli_utils.check_required_parameters
def execute(
    name, team, execution_id, operation, rest_api_url, output, arguments
) -> None:
    cmd = JobExecute(rest_api_url)
    if operation == ExecuteOperation.START:
        name = get_or_prompt("Job Name", name)
        cmd.start(name, team, output, arguments)
    elif operation == ExecuteOperation.SHOW:
        name = get_or_prompt("Job Name", name)
        execution_id = get_or_prompt("Job Execution ID", execution_id)
        cmd.show(name, team, execution_id, output)
    elif operation == ExecuteOperation.LIST:
        name = get_or_prompt("Job Name", name)
        cmd.list(name, team, output)
    elif operation == ExecuteOperation.CANCEL:
        name = get_or_prompt("Job Name", name)
        team = get_or_prompt("Job Team", team)
        execution_id = get_or_prompt("Job Execution ID", execution_id)
        cmd.cancel(name, team, execution_id)
    elif operation == ExecuteOperation.LOGS:
        name = get_or_prompt("Job Name", name)
        team = get_or_prompt("Job Team", team)
        cmd.logs(name, team, execution_id)
    elif operation == ExecuteOperation.WAIT:
        name = get_or_prompt("Job Name", name)
        # cmd.wait(name, team)
        click.echo("Operation wait not implemented")
    else:
        click.echo(
            f"No execute operation specified. "
            f"Please specify one of: {['--' + str(op.value) for op in ExecuteOperation]}"
        )
