# Copyright 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import click
from urllib3 import HTTPResponse
from vdk.internal.control.configuration.defaults_config import load_default_team_name
from vdk.internal.control.rest_lib.factory import ApiClientFactory
from vdk.internal.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from vdk.internal.control.utils import cli_utils

log = logging.getLogger(__name__)


class JobDownloadKey:
    def __init__(self, rest_api_url: str):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()

    @ApiClientErrorDecorator()
    def download(self, team: str, name: str, path: str):
        keytab_file_path = os.path.join(path, f"{name}.keytab")
        response: HTTPResponse = self.jobs_api.data_job_keytab_download(
            team_name=team, job_name=name, _preload_content=False
        )
        with open(keytab_file_path, "wb") as w:
            w.write(response.data)
        log.info(f"Saved keytab in {keytab_file_path}")


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    name="download-key",
    help="Download a Data Job keytab. A keytab is used to authenticate against the Control Service."
    "Operators of Control Service can configure default credentials for a data job to authenticate "
    "against databases or APIs used during data job run. "
    """

Examples:

\b
# This will download the data job key in directory data-jobs .
# It is recommended the the key is next to the data job directory (and not inside)
vdk download-key -n example -p /home/user/data-jobs

""",
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
    help="The path to the parent directory where the Data Job key will be downloaded."
    " If none specified it will use the current working directory."
    " It should be in the same directory as the Data Job directory.",
)
@cli_utils.rest_api_url_option()
@cli_utils.check_required_parameters
def download_key(name: str, team: str, path: str, rest_api_url: str):
    cmd = JobDownloadKey(rest_api_url)
    cmd.download(team, name, path)
