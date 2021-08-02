# Copyright (c) 2021 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import logging
import os

import click
from taurus.vdk.control.configuration.defaults_config import load_default_team_name
from taurus.vdk.control.rest_lib.factory import ApiClientFactory
from taurus.vdk.control.rest_lib.rest_client_errors import ApiClientErrorDecorator
from taurus.vdk.control.utils import cli_utils

log = logging.getLogger(__name__)


class JobDownloadKey:
    def __init__(self, rest_api_url):
        self.jobs_api = ApiClientFactory(rest_api_url).get_jobs_api()

    @ApiClientErrorDecorator()
    def download(self, team, name, path):
        keytab_file_path = os.path.join(path, f"{name}.keytab")
        response = self.jobs_api.data_job_keytab_download(
            team_name=team, job_name=name, _preload_content=False
        )
        with open(keytab_file_path, "wb") as w:
            w.write(response.data)
        log.info(f"Saved keytab in {keytab_file_path}")


# Below is the definition of the CLI API/UX users will be interacting
# Above is the actual implementation of the operations


@click.command(
    name="download-key",
    help="Download Data Job keytab. Keytab is used to authenticate against Data Plane."
    "Operators of Control Service can configure default credentials for a data job to authenticate "
    "against databases or APIs used during data job run. "
    """

Examples:

\b
# This will download the data job key in directory data-jobs .
# It is recommended the the key is next to the data job directory (and not inside)
vdkcli download-key -n example -p /home/user/data-jobs

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
@click.pass_context
@cli_utils.check_required_parameters
def download_key(ctx: click.Context, name, team, path, rest_api_url):
    cmd = JobDownloadKey(rest_api_url)
    cmd.download(team, name, path)
    pass
