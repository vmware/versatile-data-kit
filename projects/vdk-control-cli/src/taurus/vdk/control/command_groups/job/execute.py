# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import json
import logging
import os
from enum import Enum
from enum import unique

import click
from tabulate import tabulate
from taurus.vdk.control.configuration.defaults_config import load_default_team_name
from taurus.vdk.control.rest_lib.factory import ApiClientFactory
from taurus.vdk.control.utils import cli_utils
from taurus.vdk.control.utils.cli_utils import get_or_prompt
from taurus.vdk.control.utils.cli_utils import OutputFormat
from taurus_datajob_api import DataJobExecution
from taurus_datajob_api import DataJobExecutionRequest

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


class JobExecute:
    def __init__(self, rest_api_url: str):
        self.execution_api = ApiClientFactory(rest_api_url).get_execution_api()

    @staticmethod
    def __model_executions(executions, output: OutputFormat):
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

    def start(self, name: str, team: str, output: OutputFormat):
        execution_request = DataJobExecutionRequest(
            started_by=f"vdk-control-cli", args={}
        )
        log.debug(f"Starting job with request {execution_request}")
        _, _, headers = self.execution_api.data_job_execution_start_with_http_info(
            team_name=team,
            job_name=name,
            deployment_id="production",  # TODO
            data_job_execution_request=execution_request,
        )
        log.debug(f"Received headers: {headers}")

        location = headers["Location"]
        execution_id = os.path.basename(location)
        if output == OutputFormat.TEXT.value:
            log.info(
                f"Execution of Data Job {name} started. "
                f"See execution status using: \n\n"
                f"vdkcli execute --show --execution-id {execution_id} -n {name}"
            )
        elif output == OutputFormat.JSON.value:
            result = {
                "job_name": name,
                "execution_id": execution_id,
            }
            click.echo(json.dumps(result))

    def show(self, name: str, team: str, execution_id: str, output: OutputFormat):
        execution: DataJobExecution = self.execution_api.data_job_execution_read(
            team_name=team, job_name=name, execution_id=execution_id
        )
        click.echo(self.__model_executions([execution], output))

    def list(self, name: str, team: str, output: OutputFormat):
        executions: list[DataJobExecution] = self.execution_api.data_job_execution_list(
            team_name=team, job_name=name
        )
        click.echo(self.__model_executions(executions, output))


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    help="Starts execution of a data job that is deployed or check status of job execution(s). (Beta)"
    """
Examples:

\b
# Start new remote execution of Data Job 'example-job'
# As an output it will print how to get starts and it's execution ID:
vdkcli execute --start -n example-job -t "Example Team"

\b
# Check status of a currently executing Data Job:
vdkcli execute --show --execution-id example-job-1619094633811-cc49d  -n example-job -t "Example Team"

\b
# List recent execution of a Data Job:
vdkcli execute --list -n example-job -t "Example Team"
               """,
    hidden=True,
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
    "Should be printed when using vdkcli execute --start",
)
@click.option(
    "--cancel",
    "operation",
    hidden=True,
    flag_value=ExecuteOperation.CANCEL,
    help="Cancels a job execution. Requires --execution-id to be provided. "
    "Should be printed when using vdkcli execute --start",
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
    "Should be printed when using vdkcli execute --start",
)
@cli_utils.rest_api_url_option()
@cli_utils.output_option()
@cli_utils.check_required_parameters
def execute(name, team, execution_id, operation, rest_api_url, output):
    cmd = JobExecute(rest_api_url)
    if operation == ExecuteOperation.START:
        name = get_or_prompt("Job Name", name)
        cmd.start(name, team, output)
    elif operation == ExecuteOperation.SHOW:
        name = get_or_prompt("Job Name", name)
        execution_id = get_or_prompt("Job Execution ID", execution_id)
        cmd.show(name, team, execution_id, output)
    elif operation == ExecuteOperation.LIST:
        name = get_or_prompt("Job Name", name)
        cmd.list(name, team, output)
    elif operation == ExecuteOperation.CANCEL:
        name = get_or_prompt("Job Name", name)
        # cmd.cancel(name, team)
        click.echo("Operation cancel not implemented")
    elif operation == ExecuteOperation.WAIT:
        name = get_or_prompt("Job Name", name)
        # cmd.wait(name, team)
        click.echo("Operation wait not implemented")
    else:
        click.echo(
            f"No execute operation specified. "
            f"Please specify one of: {['--' + str(op.value) for op in ExecuteOperation]}"
        )
