# Copyright 2021-2023 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0
import click
from vdk.plugin.control_api_auth.auth_config import AuthConfigFolder


@click.command(
    short_help="Logout the user from the Control Service.",
    help="Logout the user from the Control Service by deleting their refresh token stored locally.",
)
def logout():
    conf = AuthConfigFolder()
    conf.delete_credentials()
